package com.streampro.app;

import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import android.os.Handler;
import android.os.Looper;
import androidx.core.content.FileProvider;

import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;

// Scarica l'APK di aggiornamento e avvia direttamente l'installer di sistema
// (Intent su un content:// URI via FileProvider, già configurato in
// AndroidManifest.xml/file_paths.xml per altri usi), invece di passare dal
// browser di sistema (window.open(url, '_system')) come faceva prima —
// quest'ultimo richiedeva di uscire dall'app, aspettare il download nel
// browser, e aprire manualmente le Notifiche/Download per installare.
// Il tocco finale di conferma "Installa" resta comunque obbligatorio: è un
// limite di sicurezza di Android per gli APK non di sistema, non aggirabile
// da nessuna app, nemmeno con questo plugin.
@CapacitorPlugin(name = "ApkInstaller")
public class ApkInstallerPlugin extends Plugin {

    @PluginMethod
    public void downloadAndInstall(PluginCall call) {
        String url = call.getString("url");
        if (url == null || url.isEmpty()) {
            call.reject("URL mancante");
            return;
        }

        Context context = getContext();
        File cacheDir = context.getCacheDir();

        // Ripulisce eventuali APK scaricati da aggiornamenti precedenti prima
        // di scaricarne uno nuovo: nessun file "orfano" si accumula nel
        // tempo, ed è più sicuro di cancellare l'APK appena scaricato subito
        // dopo averlo aperto (l'installer potrebbe non aver ancora finito di
        // leggerlo).
        File[] leftovers = cacheDir.listFiles((dir, name) -> name.startsWith("update-") && name.endsWith(".apk"));
        if (leftovers != null) {
            for (File f : leftovers) {
                //noinspection ResultOfMethodCallIgnored
                f.delete();
            }
        }

        File outFile = new File(cacheDir, "update-" + System.currentTimeMillis() + ".apk");

        new Thread(() -> {
            try {
                URL u = new URL(url);
                HttpURLConnection conn = (HttpURLConnection) u.openConnection();
                conn.setRequestMethod("GET");
                conn.setConnectTimeout(15000);
                conn.setReadTimeout(30000);
                conn.connect();

                int responseCode = conn.getResponseCode();
                if (responseCode != HttpURLConnection.HTTP_OK) {
                    conn.disconnect();
                    new Handler(Looper.getMainLooper()).post(() ->
                        call.reject("Download fallito: HTTP " + responseCode));
                    return;
                }

                try (InputStream in = conn.getInputStream();
                     FileOutputStream out = new FileOutputStream(outFile)) {
                    byte[] buffer = new byte[8192];
                    int read;
                    while ((read = in.read(buffer)) != -1) {
                        out.write(buffer, 0, read);
                    }
                }
                conn.disconnect();

                new Handler(Looper.getMainLooper()).post(() -> {
                    try {
                        Uri apkUri = FileProvider.getUriForFile(
                            context,
                            context.getPackageName() + ".fileprovider",
                            outFile
                        );
                        Intent intent = new Intent(Intent.ACTION_VIEW);
                        intent.setDataAndType(apkUri, "application/vnd.android.package-archive");
                        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
                        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                        context.startActivity(intent);

                        JSObject result = new JSObject();
                        result.put("started", true);
                        call.resolve(result);

                        // L'installer di sistema legge il file mentre l'utente conferma
                        // il tocco finale: cancellarlo troppo presto lo interromperebbe.
                        // Un ritardo di un minuto è ampiamente sufficiente, e comunque
                        // il prossimo controllo aggiornamenti ripulisce quello che resta.
                        new Handler(Looper.getMainLooper()).postDelayed(() -> {
                            //noinspection ResultOfMethodCallIgnored
                            outFile.delete();
                        }, 60000);
                    } catch (Exception e) {
                        call.reject("Impossibile avviare l'installer: " + e.getMessage());
                    }
                });
            } catch (Exception e) {
                new Handler(Looper.getMainLooper()).post(() ->
                    call.reject("Errore durante il download: " + e.getMessage()));
            }
        }).start();
    }
}
