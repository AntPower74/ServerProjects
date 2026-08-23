// JATUA Dark — Triple-A Next-Gen Combat Flight Simulator
// Inspired by: Star Citizen (ArcCorp Area18), Cyberpunk 2077, Ace Combat 7 & Project Wingman
// Features: Holographic 3D Billboards, Sky-Trains, Industrial Steam Vents, Transonic Vapor Cones,
// Wingtip Vortices, High-G G-LOC screen effects, Authentic Combat HUD, PBR Megacity

let scene, camera, renderer, clock, controls;
let spaceshipGroup, cityGroup, particleGroup, projectileGroup, explosionGroup;
let cloudGroup, trafficGroup, hologramGroup, steamGroup, trainGroup;
let thrusterMesh, thrusterLight, flameCore, flameDiamonds = [];
let thrusterParticles = [], projectiles = [], explosions = [];
let trafficVehicles = [], steamPuffs = [], skyTrains = [];
let wingtipTrails = { left: [], right: [] };
let vaporConeMesh;

// Textures
let glassFacadeTex, brutalistFacadeTex, holoTexture1, holoTexture2;

// Moving Control Surfaces
let upperRightFinMesh, upperLeftFinMesh, lowerRightFinMesh, lowerLeftFinMesh;

// Audio Synthesizer via Web Audio API
let audioCtx = null;
let audioEnabled = false;
let engineGainNode = null, engineOsc = null;

// Serpentine Flight Canyon
function getCanyonCenterX(z) {
    return Math.sin(z * 0.0015) * 180;
}

function getCanyonCenterY(z) {
    return 360 + Math.cos(z * 0.0018) * 80;
}

// Flight State
const flightState = {
    mode: 'cinematic',
    pos: new THREE.Vector3(0, 360, 0),
    speed: 160,
    maxSpeed: 480,
    minSpeed: 90,
    gForce: 1.0,
    pitch: 0,
    roll: 0,
    yaw: 0,
    activeManeuver: null,
    maneuverTime: 0,
    camMode: 'action',
    currentFlybyPos: new THREE.Vector3(),
    highGTime: 0
};

const inputState = {
    pitchUp: false,
    pitchDown: false,
    rollLeft: false,
    rollRight: false,
    yawLeft: false,
    yawRight: false,
    boost: false,
    fire: false,
    touchX: 0,
    touchY: 0
};

// Video Recorder
let mediaRecorder = null;
let recordedChunks = [];
let isRecording = false;

window.addEventListener('DOMContentLoaded', () => {
    initThree();
    generateAAAProceduralTextures();
    buildHighDetailJatuaSpaceship();
    buildStarCitizenStyleMegacity();
    buildHolographicBillboards();
    buildSkyTrainMonorails();
    buildIndustrialSteamVents();
    buildAtmosphericCloudBanks();
    buildCanyonTrafficSystem();
    buildCinematicEnvironmentLighting();
    setupEventListeners();
    setupMobileTouch();
    setupAudioSynth();
    animate();
});

function initThree() {
    const container = document.getElementById('canvas-container');
    scene = new THREE.Scene();
    
    // Blade Runner 2049 / Star Citizen Moody Atmospheric Palette
    const fogColor = new THREE.Color(0x0c151a);
    scene.background = fogColor;
    scene.fog = new THREE.FogExp2(fogColor, 0.00105);

    camera = new THREE.PerspectiveCamera(56, window.innerWidth / window.innerHeight, 0.5, 6000);
    camera.position.set(0, 370, 52);

    renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.2;
    renderer.outputEncoding = THREE.sRGBEncoding;
    container.appendChild(renderer.domElement);

    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enabled = false;
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;

    clock = new THREE.Clock();

    cityGroup = new THREE.Group();
    scene.add(cityGroup);

    hologramGroup = new THREE.Group();
    scene.add(hologramGroup);

    trainGroup = new THREE.Group();
    scene.add(trainGroup);

    steamGroup = new THREE.Group();
    scene.add(steamGroup);

    cloudGroup = new THREE.Group();
    scene.add(cloudGroup);

    trafficGroup = new THREE.Group();
    scene.add(trafficGroup);

    particleGroup = new THREE.Group();
    scene.add(particleGroup);

    projectileGroup = new THREE.Group();
    scene.add(projectileGroup);

    explosionGroup = new THREE.Group();
    scene.add(explosionGroup);

    window.addEventListener('resize', onWindowResize);
}

function buildCinematicEnvironmentLighting() {
    const hemiLight = new THREE.HemisphereLight(0x769eb3, 0x111c22, 1.15);
    scene.add(hemiLight);

    const sunLight = new THREE.DirectionalLight(0xd9ecf8, 1.7);
    sunLight.position.set(300, 900, 400);
    scene.add(sunLight);

    const rimLight = new THREE.DirectionalLight(0x193744, 0.95);
    rimLight.position.set(-350, -250, -200);
    scene.add(rimLight);
}

// -------------------------------------------------------------
// PROCEDURAL AAA TEXTURES (CYBERPUNK 2077 & STAR CITIZEN STYLE)
// -------------------------------------------------------------
function generateAAAProceduralTextures() {
    // 1. High-Tech Glass & Steel Monolith Facade
    const canvasGlass = document.createElement('canvas');
    canvasGlass.width = 512;
    canvasGlass.height = 1024;
    const ctxG = canvasGlass.getContext('2d');

    ctxG.fillStyle = '#162025';
    ctxG.fillRect(0, 0, 512, 1024);

    // Mullions
    ctxG.fillStyle = '#0e1418';
    for (let x = 0; x < 512; x += 32) {
        ctxG.fillRect(x, 0, 4, 1024);
    }

    // Spandrel floor dividers
    for (let y = 0; y < 1024; y += 48) {
        ctxG.fillStyle = '#222d33';
        ctxG.fillRect(0, y, 512, 10);
        ctxG.fillStyle = '#0b1013';
        ctxG.fillRect(0, y + 10, 512, 2);
    }

    // Windows with Warm/Cool Interior Luminosity
    const windowPalettes = [
        ['#fff3cd', '#ffeaa7', '#fed330'],
        ['#e0f2fe', '#bae6fd', '#7dd3fc'],
        ['#f8fafc', '#e2e8f0', '#cbd5e1']
    ];

    for (let y = 14; y < 1010; y += 48) {
        if (Math.random() < 0.12) continue;
        for (let x = 6; x < 500; x += 32) {
            if (Math.random() < 0.48) {
                const palette = windowPalettes[Math.floor(Math.random() * windowPalettes.length)];
                const col = palette[Math.floor(Math.random() * palette.length)];
                ctxG.fillStyle = col;
                ctxG.fillRect(x, y, 22, 32);

                if (Math.random() > 0.4) {
                    ctxG.fillStyle = 'rgba(15, 23, 28, 0.4)';
                    ctxG.fillRect(x, y, 22, Math.random() * 18);
                }
            }
        }
    }
    glassFacadeTex = new THREE.CanvasTexture(canvasGlass);
    glassFacadeTex.wrapS = THREE.RepeatWrapping;
    glassFacadeTex.wrapT = THREE.RepeatWrapping;

    // 2. Brutalist Concrete & Mechanical Panels
    const canvasBrut = document.createElement('canvas');
    canvasBrut.width = 512;
    canvasBrut.height = 512;
    const ctxB = canvasBrut.getContext('2d');
    ctxB.fillStyle = '#222b31';
    ctxB.fillRect(0, 0, 512, 512);

    for (let x = 0; x < 512; x += 16) {
        ctxB.fillStyle = '#182024';
        ctxB.fillRect(x, 0, 6, 512);
        ctxB.fillStyle = '#2d3840';
        ctxB.fillRect(x + 6, 0, 4, 512);
    }
    for (let y = 0; y < 512; y += 64) {
        ctxB.fillStyle = '#10161a';
        ctxB.fillRect(0, y, 512, 8);
    }
    brutalistFacadeTex = new THREE.CanvasTexture(canvasBrut);
    brutalistFacadeTex.wrapS = THREE.RepeatWrapping;
    brutalistFacadeTex.wrapT = THREE.RepeatWrapping;

    // 3. Cyberpunk Hologram Ad Textures (Cyan Corporate Grid & Japanese Tech Kanji)
    const canvasHolo1 = document.createElement('canvas');
    canvasHolo1.width = 512;
    canvasHolo1.height = 256;
    const ctxH1 = canvasHolo1.getContext('2d');
    ctxH1.fillStyle = 'rgba(0, 229, 255, 0.12)';
    ctxH1.fillRect(0, 0, 512, 256);
    ctxH1.strokeStyle = '#00e5ff';
    ctxH1.lineWidth = 4;
    ctxH1.strokeRect(8, 8, 496, 240);
    ctxH1.fillStyle = '#00e5ff';
    ctxH1.font = 'bold 36px monospace';
    ctxH1.fillText('ARCCORP // AEROSPACE', 30, 80);
    ctxH1.font = '22px monospace';
    ctxH1.fillStyle = '#e0f2fe';
    ctxH1.fillText('QUANTUM DRIVE SYNDICATE v8.4', 30, 140);
    ctxH1.fillText('[ SYSTEM NORMAL - SECTOR 18 ]', 30, 190);
    holoTexture1 = new THREE.CanvasTexture(canvasHolo1);

    const canvasHolo2 = document.createElement('canvas');
    canvasHolo2.width = 512;
    canvasHolo2.height = 256;
    const ctxH2 = canvasHolo2.getContext('2d');
    ctxH2.fillStyle = 'rgba(234, 179, 8, 0.12)';
    ctxH2.fillRect(0, 0, 512, 256);
    ctxH2.strokeStyle = '#eab308';
    ctxH2.lineWidth = 4;
    ctxH2.strokeRect(8, 8, 496, 240);
    ctxH2.fillStyle = '#facc15';
    ctxH2.font = 'bold 40px sans-serif';
    ctxH2.fillText('重工 重工業 // KAWASAKI HYPER', 24, 90);
    ctxH2.font = 'bold 24px monospace';
    ctxH2.fillStyle = '#fef08a';
    ctxH2.fillText('PLASMA INJECTION // 99.8% STABLE', 24, 160);
    holoTexture2 = new THREE.CanvasTexture(canvasHolo2);
}

// -------------------------------------------------------------
// PHOTOREALISTIC MEGASTRUCTURE CITY (STAR CITIZEN STYLE)
// -------------------------------------------------------------
function buildStarCitizenStyleMegacity() {
    const glassMat = new THREE.MeshStandardMaterial({
        map: glassFacadeTex,
        color: 0x9cb5c2,
        metalness: 0.65,
        roughness: 0.38,
        flatShading: true
    });

    const brutalistMat = new THREE.MeshStandardMaterial({
        map: brutalistFacadeTex,
        color: 0x6c7f89,
        metalness: 0.35,
        roughness: 0.65,
        flatShading: true
    });

    const darkSteelMat = new THREE.MeshStandardMaterial({
        color: 0x162026,
        metalness: 0.85,
        roughness: 0.25
    });

    const skybridgeMat = new THREE.MeshStandardMaterial({
        color: 0x1e2a31,
        metalness: 0.8,
        roughness: 0.35
    });

    const numClusters = 270;
    const zRange = 6800;

    for (let i = 0; i < numClusters; i++) {
        const z = (Math.random() - 0.5) * zRange;
        const canyonCenter = getCanyonCenterX(z);

        const isLeft = Math.random() > 0.5;
        const offset = 370 + Math.random() * 900;
        const x = isLeft ? (canyonCenter - offset) : (canyonCenter + offset);

        const baseW = 110 + Math.random() * 150;
        const baseD = 110 + Math.random() * 150;
        const totalH = 420 + Math.random() * 1000;

        // 1. Massive Ground Podium Base
        const podiumH = totalH * 0.45;
        const podiumGeo = new THREE.BoxGeometry(baseW, podiumH, baseD);
        const pMat = brutalistMat.clone();
        pMat.map = brutalistFacadeTex.clone();
        pMat.map.repeat.set(baseW / 40, podiumH / 50);
        pMat.map.needsUpdate = true;
        const podiumMesh = new THREE.Mesh(podiumGeo, pMat);
        podiumMesh.position.set(x, podiumH / 2, z);
        cityGroup.add(podiumMesh);

        // 2. High-Rise Tower Shaft
        const towerW = baseW * 0.72;
        const towerD = baseD * 0.72;
        const towerH = totalH * 0.42;
        const towerGeo = new THREE.BoxGeometry(towerW, towerH, towerD);
        const gMat = glassMat.clone();
        gMat.map = glassFacadeTex.clone();
        gMat.map.repeat.set(towerW / 30, towerH / 60);
        gMat.map.needsUpdate = true;
        const towerMesh = new THREE.Mesh(towerGeo, gMat);
        towerMesh.position.set(x, podiumH + towerH / 2, z);
        cityGroup.add(towerMesh);

        // 3. Stepped Rooftop Crown
        const crownW = towerW * 0.65;
        const crownD = towerD * 0.65;
        const crownH = totalH * 0.13;
        const crownGeo = new THREE.BoxGeometry(crownW, crownH, crownD);
        const crownMesh = new THREE.Mesh(crownGeo, darkSteelMat);
        crownMesh.position.set(x, podiumH + towerH + crownH / 2, z);
        cityGroup.add(crownMesh);

        // 4. Vertical Structural Buttress Columns
        const buttressW = 15 + Math.random() * 12;
        const buttressGeo = new THREE.BoxGeometry(buttressW, (podiumH + towerH) * 0.95, baseD + 14);
        const buttressMesh = new THREE.Mesh(buttressGeo, darkSteelMat);
        buttressMesh.position.set(x, (podiumH + towerH) * 0.48, z);
        cityGroup.add(buttressMesh);

        const topY = podiumH + towerH + crownH;

        // 5. Aviation Communication Masts with Pulsing Beacons
        if (Math.random() > 0.25) {
            const mastH = 65 + Math.random() * 140;
            const mastGeo = new THREE.CylinderGeometry(0.8, 3.2, mastH, 6);
            const mast = new THREE.Mesh(mastGeo, darkSteelMat);
            mast.position.set(x, topY + mastH / 2, z);
            cityGroup.add(mast);

            const beaconGeo = new THREE.SphereGeometry(2.5, 6, 6);
            const beaconMat = new THREE.MeshBasicMaterial({ color: 0xef4444 });
            const beacon = new THREE.Mesh(beaconGeo, beaconMat);
            beacon.position.set(x, topY + mastH, z);
            cityGroup.add(beacon);
        }

        // 6. Rooftop Helipad with Glowing Perimeter
        if (Math.random() > 0.55 && crownW > 45) {
            const padGeo = new THREE.CylinderGeometry(crownW * 0.42, crownW * 0.42, 1.2, 16);
            const padMat = new THREE.MeshStandardMaterial({ color: 0x1f272e, roughness: 0.6 });
            const pad = new THREE.Mesh(padGeo, padMat);
            pad.position.set(x, topY + 0.6, z);
            cityGroup.add(pad);

            const hGeo = new THREE.PlaneGeometry(14, 14);
            const hMat = new THREE.MeshBasicMaterial({ color: 0xfacc15, transparent: true, opacity: 0.9 });
            const hMesh = new THREE.Mesh(hGeo, hMat);
            hMesh.rotation.x = -Math.PI / 2;
            hMesh.position.set(x, topY + 1.3, z);
            cityGroup.add(hMesh);
        }

        // 7. High-Altitude Skybridges
        if (Math.random() > 0.82 && offset < 580) {
            const bridgeL = 230 + Math.random() * 170;
            const bridgeGeo = new THREE.BoxGeometry(bridgeL, 18, 26);
            const bridgeMesh = new THREE.Mesh(bridgeGeo, skybridgeMat);
            const bridgeY = 280 + Math.random() * 320;
            bridgeMesh.position.set(x + (isLeft ? 115 : -115), bridgeY, z);
            cityGroup.add(bridgeMesh);
        }
    }

    // Canyon Floor Grid
    const groundGeo = new THREE.PlaneGeometry(12000, 12000);
    const groundMat = new THREE.MeshStandardMaterial({
        color: 0x04080b,
        metalness: 0.95,
        roughness: 0.85
    });
    const ground = new THREE.Mesh(groundGeo, groundMat);
    ground.rotation.x = -Math.PI / 2;
    scene.add(ground);
}

// -------------------------------------------------------------
// HOLOGRAPHIC BILLBOARDS & GLOWING ADVERTS (CYBERPUNK STYLE)
// -------------------------------------------------------------
function buildHolographicBillboards() {
    const holoMat1 = new THREE.MeshBasicMaterial({
        map: holoTexture1,
        transparent: true,
        opacity: 0.85,
        side: THREE.DoubleSide
    });

    const holoMat2 = new THREE.MeshBasicMaterial({
        map: holoTexture2,
        transparent: true,
        opacity: 0.85,
        side: THREE.DoubleSide
    });

    const numHolos = 32;
    for (let i = 0; i < numHolos; i++) {
        const z = -2800 + (i / numHolos) * 5600;
        const canyonX = getCanyonCenterX(z);
        const isLeft = (i % 2 === 0);
        const x = canyonX + (isLeft ? -380 : 380);
        const y = 300 + (i % 5) * 60;

        const hW = 140;
        const hH = 70;
        const hGeo = new THREE.PlaneGeometry(hW, hH);
        const mesh = new THREE.Mesh(hGeo, isLeft ? holoMat1 : holoMat2);
        mesh.position.set(x, y, z);
        mesh.rotation.y = isLeft ? Math.PI / 2 + 0.15 : -Math.PI / 2 - 0.15;
        hologramGroup.add(mesh);
    }
}

// -------------------------------------------------------------
// HIGH-SPEED SKY-TRAIN / MONORAIL NETWORK
// -------------------------------------------------------------
function buildSkyTrainMonorails() {
    const trackMat = new THREE.MeshStandardMaterial({ color: 0x1a242a, metalness: 0.9, roughness: 0.3 });
    const trainMat = new THREE.MeshBasicMaterial({ color: 0x38bdf8 });

    // Build 2 elevated monorail tubes along canyon sides
    [-290, 290].forEach((xSide, idx) => {
        const numSegments = 40;
        const trackGeo = new THREE.BoxGeometry(10, 8, 6000);
        const trackMesh = new THREE.Mesh(trackGeo, trackMat);
        trackMesh.position.set(xSide, 240, 0);
        trainGroup.add(trackMesh);

        // Sky-train cars
        const carGeo = new THREE.BoxGeometry(8, 7, 75);
        const carMesh = new THREE.Mesh(carGeo, trainMat);
        carMesh.position.set(xSide, 244, (idx === 0 ? -1200 : 1200));
        trainGroup.add(carMesh);

        skyTrains.push({
            mesh: carMesh,
            speed: idx === 0 ? 320 : -320
        });
    });
}

function updateSkyTrains(delta) {
    skyTrains.forEach(t => {
        t.mesh.position.z += t.speed * delta;
        if (t.mesh.position.z > 2900) t.mesh.position.z = -2900;
        if (t.mesh.position.z < -2900) t.mesh.position.z = 2900;
    });
}

// -------------------------------------------------------------
// INDUSTRIAL BILLOWING STEAM VENTS
// -------------------------------------------------------------
function buildIndustrialSteamVents() {
    const steamMat = new THREE.MeshBasicMaterial({
        color: 0x8ba6b5,
        transparent: true,
        opacity: 0.18,
        depthWrite: false
    });

    const numVents = 24;
    for (let i = 0; i < numVents; i++) {
        const z = -2600 + (i / numVents) * 5200;
        const canyonX = getCanyonCenterX(z);
        const isLeft = Math.random() > 0.5;
        const x = canyonX + (isLeft ? -360 : 360);
        const y = 200 + Math.random() * 250;

        const puffGeo = new THREE.SphereGeometry(14, 6, 6);
        const puff = new THREE.Mesh(puffGeo, steamMat);
        puff.position.set(x, y, z);
        steamGroup.add(puff);

        steamPuffs.push({
            mesh: puff,
            baseY: y,
            speedY: 15 + Math.random() * 15,
            driftX: (Math.random() - 0.5) * 6
        });
    }
}

function updateSteam(delta) {
    steamPuffs.forEach(s => {
        s.mesh.position.y += s.speedY * delta;
        s.mesh.position.x += s.driftX * delta;
        s.mesh.scale.multiplyScalar(1.008);
        if (s.mesh.position.y > s.baseY + 120) {
            s.mesh.position.y = s.baseY;
            s.mesh.scale.set(1, 1, 1);
        }
    });
}

// -------------------------------------------------------------
// ATMOSPHERIC CLOUDS & CANYON TRAFFIC
// -------------------------------------------------------------
function buildAtmosphericCloudBanks() {
    const cloudMat = new THREE.MeshBasicMaterial({
        color: 0x3d5460,
        transparent: true,
        opacity: 0.16,
        depthWrite: false
    });

    const numClouds = 70;
    for (let i = 0; i < numClouds; i++) {
        const cloudW = 260 + Math.random() * 360;
        const cloudD = 260 + Math.random() * 360;
        const cloudH = 45 + Math.random() * 85;

        const cGeo = new THREE.BoxGeometry(cloudW, cloudH, cloudD);
        const cloud = new THREE.Mesh(cGeo, cloudMat);

        const z = (Math.random() - 0.5) * 5800;
        const x = getCanyonCenterX(z) + (Math.random() - 0.5) * 800;
        const y = 220 + Math.random() * 260;

        cloud.position.set(x, y, z);
        cloudGroup.add(cloud);
    }
}

function buildCanyonTrafficSystem() {
    const headLightMat = new THREE.MeshBasicMaterial({ color: 0xe0f2fe });
    const tailLightMat = new THREE.MeshBasicMaterial({ color: 0xef4444 });
    const droneHullMat = new THREE.MeshBasicMaterial({ color: 0x0f172a });

    const numVehicles = 130;
    for (let i = 0; i < numVehicles; i++) {
        const vehicle = new THREE.Group();

        const hullGeo = new THREE.BoxGeometry(4.2, 1.6, 11.0);
        const hull = new THREE.Mesh(hullGeo, droneHullMat);
        vehicle.add(hull);

        const headGeo = new THREE.SphereGeometry(0.6, 4, 4);
        const hl1 = new THREE.Mesh(headGeo, headLightMat);
        hl1.position.set(1.4, 0, -5.6);
        vehicle.add(hl1);
        const hl2 = hl1.clone();
        hl2.position.set(-1.4, 0, -5.6);
        vehicle.add(hl2);

        const tailGeo = new THREE.SphereGeometry(0.6, 4, 4);
        const tl1 = new THREE.Mesh(tailGeo, tailLightMat);
        tl1.position.set(1.4, 0, 5.6);
        vehicle.add(tl1);
        const tl2 = tl1.clone();
        tl2.position.set(-1.4, 0, 5.6);
        vehicle.add(tl2);

        const isNorthbound = Math.random() > 0.5;
        const z = (Math.random() - 0.5) * 5800;
        const canyonX = getCanyonCenterX(z);
        const laneOffset = isNorthbound ? -85 - Math.random() * 60 : 85 + Math.random() * 60;
        const y = 80 + Math.random() * 110;

        vehicle.position.set(canyonX + laneOffset, y, z);
        if (isNorthbound) vehicle.rotation.y = Math.PI;

        trafficGroup.add(vehicle);
        trafficVehicles.push({
            mesh: vehicle,
            speed: 65 + Math.random() * 75,
            direction: isNorthbound ? 1 : -1
        });
    }
}

function updateTraffic(delta) {
    trafficVehicles.forEach(v => {
        v.mesh.position.z += v.speed * v.direction * delta;
        if (v.mesh.position.z > 3000) v.mesh.position.z = -3000;
        if (v.mesh.position.z < -3000) v.mesh.position.z = 3000;
    });
}

// -------------------------------------------------------------
// AUTHENTIC JATUA DARK NEEDLE DART RECONSTRUCTION
// -------------------------------------------------------------
function buildHighDetailJatuaSpaceship() {
    spaceshipGroup = new THREE.Group();

    const hullMat = new THREE.MeshStandardMaterial({
        color: 0x667676,
        metalness: 0.48,
        roughness: 0.45,
        flatShading: true
    });

    const stealthChineMat = new THREE.MeshStandardMaterial({
        color: 0x445252,
        metalness: 0.65,
        roughness: 0.35,
        flatShading: true
    });

    const dorsalSpineMat = new THREE.MeshStandardMaterial({
        color: 0x303a3a,
        metalness: 0.75,
        roughness: 0.28
    });

    const nozzleMat = new THREE.MeshStandardMaterial({
        color: 0x202828,
        metalness: 0.9,
        roughness: 0.2
    });

    const hudSlitMat = new THREE.MeshBasicMaterial({ color: 0x00f0ff });

    // 1. Monocoque Needle Fuselage
    const slices = [
        { z: -20.0, w: 0.04, h: 0.04, yOff: 0.0 },
        { z: -14.0, w: 0.55, h: 0.38, yOff: 0.0 },
        { z: -7.0,  w: 1.25, h: 0.78, yOff: 0.04 },
        { z: 0.0,   w: 1.80, h: 1.10, yOff: 0.08 },
        { z: 5.5,   w: 1.95, h: 1.24, yOff: 0.10 },
        { z: 8.5,   w: 1.55, h: 1.08, yOff: 0.06 }
    ];

    const bodyGeo = new THREE.BufferGeometry();
    const vertices = [];
    const indices = [];

    slices.forEach((s) => {
        const halfW = s.w;
        const halfH = s.h;
        const y = s.yOff;

        vertices.push(
            -halfW * 0.55, y + halfH, s.z,
             halfW * 0.55, y + halfH, s.z,
             halfW,        y + halfH * 0.25, s.z,
             halfW * 0.9,  y - halfH * 0.3, s.z,
             halfW * 0.5,  y - halfH * 0.85, s.z,
             0,            y - halfH, s.z,
            -halfW * 0.5,  y - halfH * 0.85, s.z,
            -halfW * 0.9,  y - halfH * 0.3, s.z,
            -halfW,        y + halfH * 0.25, s.z,
            -halfW * 0.55, y + halfH, s.z
        );
    });

    for (let i = 0; i < slices.length - 1; i++) {
        const ring1 = i * 10;
        const ring2 = (i + 1) * 10;
        for (let j = 0; j < 9; j++) {
            const a = ring1 + j;
            const b = ring1 + j + 1;
            const c = ring2 + j + 1;
            const d = ring2 + j;
            indices.push(a, b, c);
            indices.push(a, c, d);
        }
    }

    bodyGeo.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
    bodyGeo.setIndex(indices);
    bodyGeo.computeVertexNormals();

    const mainFuselage = new THREE.Mesh(bodyGeo, hullMat);
    spaceshipGroup.add(mainFuselage);

    // 2. Razor Side Chine Inlays
    const chineShape = new THREE.Shape();
    chineShape.moveTo(0, 0);
    chineShape.lineTo(1.1, 7.5);
    chineShape.lineTo(0, 8.5);
    chineShape.closePath();
    const chineGeo = new THREE.ExtrudeGeometry(chineShape, { depth: 0.07, bevelEnabled: false });
    chineGeo.rotateX(Math.PI / 2);

    const rightChine = new THREE.Mesh(chineGeo, stealthChineMat);
    rightChine.position.set(1.5, 0.15, -1.0);
    spaceshipGroup.add(rightChine);

    const leftChine = rightChine.clone();
    leftChine.scale.set(-1, 1, 1);
    leftChine.position.set(-1.5, 0.15, -1.0);
    spaceshipGroup.add(leftChine);

    // 3. Dorsal Spine Fairing
    const spineGeo = new THREE.BufferGeometry();
    const spineVerts = new Float32Array([
        0, 1.4, 0.5,
        0, 1.82, 6.5,
        0.38, 1.15, 6.5,
        -0.38, 1.15, 6.5,
        0, 1.35, 8.2
    ]);
    const spineIndices = [
        0, 1, 2,  0, 3, 1,
        1, 4, 2,  1, 3, 4
    ];
    spineGeo.setAttribute('position', new THREE.BufferAttribute(spineVerts, 3));
    spineGeo.setIndex(spineIndices);
    spineGeo.computeVertexNormals();
    const spineMesh = new THREE.Mesh(spineGeo, dorsalSpineMat);
    spaceshipGroup.add(spineMesh);

    const sensorGeo = new THREE.BoxGeometry(0.08, 0.08, 2.5);
    const sensorMesh = new THREE.Mesh(sensorGeo, hudSlitMat);
    sensorMesh.position.set(0, 1.55, 3.2);
    sensorMesh.rotation.x = -0.08;
    spaceshipGroup.add(sensorMesh);

    // 4. The 4 Original Canted Stabilizers
    function createStabilizerFin() {
        const group = new THREE.Group();
        const finShape = new THREE.Shape();
        finShape.moveTo(0, 0);
        finShape.lineTo(2.8, 1.7);
        finShape.lineTo(2.4, 3.5);
        finShape.lineTo(0, 2.8);
        finShape.closePath();

        const extrudeOpts = { depth: 0.11, bevelEnabled: true, bevelSegments: 1, bevelSize: 0.03, bevelThickness: 0.03 };
        const finGeo = new THREE.ExtrudeGeometry(finShape, extrudeOpts);
        finGeo.rotateX(Math.PI / 2);
        const finMesh = new THREE.Mesh(finGeo, hullMat);
        group.add(finMesh);
        return group;
    }

    upperRightFinMesh = createStabilizerFin();
    upperRightFinMesh.position.set(0.92, 0.46, 4.4);
    upperRightFinMesh.rotation.z = -0.75;
    spaceshipGroup.add(upperRightFinMesh);

    upperLeftFinMesh = createStabilizerFin();
    upperLeftFinMesh.scale.set(-1, 1, 1);
    upperLeftFinMesh.position.set(-0.92, 0.46, 4.4);
    upperLeftFinMesh.rotation.z = 0.75;
    spaceshipGroup.add(upperLeftFinMesh);

    lowerRightFinMesh = createStabilizerFin();
    lowerRightFinMesh.position.set(0.88, -0.32, 4.7);
    lowerRightFinMesh.rotation.z = -2.35;
    spaceshipGroup.add(lowerRightFinMesh);

    lowerLeftFinMesh = createStabilizerFin();
    lowerLeftFinMesh.scale.set(-1, 1, 1);
    lowerLeftFinMesh.position.set(-0.88, -0.32, 4.7);
    lowerLeftFinMesh.rotation.z = 2.35;
    spaceshipGroup.add(lowerLeftFinMesh);

    // 5. Rear Nozzle Shroud
    const nozzleGeo = new THREE.CylinderGeometry(0.95, 1.15, 1.4, 16, 1, true);
    nozzleGeo.rotateX(Math.PI / 2);
    nozzleGeo.translate(0, 0.1, 9.0);
    const nozzleMesh = new THREE.Mesh(nozzleGeo, nozzleMat);
    spaceshipGroup.add(nozzleMesh);

    // 6. Transonic Prandtl-Glauert Vapor Cone (Ace Combat 7 Style)
    const coneGeo = new THREE.ConeGeometry(3.6, 6.0, 16, 1, true);
    coneGeo.rotateX(Math.PI / 2);
    coneGeo.translate(0, 0.1, -1.0);
    const vaporMat = new THREE.MeshBasicMaterial({
        color: 0xffffff,
        transparent: true,
        opacity: 0.0,
        side: THREE.DoubleSide
    });
    vaporConeMesh = new THREE.Mesh(coneGeo, vaporMat);
    spaceshipGroup.add(vaporConeMesh);

    // 7. Ethereal Blue-Cyan Plasma Jet Stream + Shock Diamonds
    const flameGeo = new THREE.ConeGeometry(0.88, 12.0, 12);
    flameGeo.rotateX(-Math.PI / 2);
    flameGeo.translate(0, 0.1, 15.2);
    const flameMat = new THREE.MeshBasicMaterial({
        color: 0x38bdf8,
        transparent: true,
        opacity: 0.72
    });
    thrusterMesh = new THREE.Mesh(flameGeo, flameMat);
    spaceshipGroup.add(thrusterMesh);

    const coreGeo = new THREE.ConeGeometry(0.40, 7.0, 8);
    coreGeo.rotateX(-Math.PI / 2);
    coreGeo.translate(0, 0.1, 12.8);
    const coreMat = new THREE.MeshBasicMaterial({
        color: 0xf0faff,
        transparent: true,
        opacity: 0.95
    });
    flameCore = new THREE.Mesh(coreGeo, coreMat);
    spaceshipGroup.add(flameCore);

    for (let d = 0; d < 3; d++) {
        const diaGeo = new THREE.OctahedronGeometry(0.24 - d * 0.05);
        const diaMat = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.85 });
        const diamond = new THREE.Mesh(diaGeo, diaMat);
        diamond.position.set(0, 0.1, 10.5 + d * 2.2);
        spaceshipGroup.add(diamond);
        flameDiamonds.push(diamond);
    }

    thrusterLight = new THREE.PointLight(0x38bdf8, 4.0, 60);
    thrusterLight.position.set(0, 0.1, 12.0);
    spaceshipGroup.add(thrusterLight);

    spaceshipGroup.position.copy(flightState.pos);
    scene.add(spaceshipGroup);
}

// -------------------------------------------------------------
// AUDIO SYNTHESIZER
// -------------------------------------------------------------
function setupAudioSynth() {
    document.getElementById('btn-audio').addEventListener('click', () => {
        if (!audioCtx) {
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            startEngineSound();
            audioEnabled = true;
            document.getElementById('btn-audio').classList.add('active');
            document.getElementById('btn-audio').textContent = '🔊 Audio Attivo';
        } else if (audioCtx.state === 'suspended') {
            audioCtx.resume();
            audioEnabled = true;
            document.getElementById('btn-audio').classList.add('active');
        } else {
            audioCtx.suspend();
            audioEnabled = false;
            document.getElementById('btn-audio').classList.remove('active');
            document.getElementById('btn-audio').textContent = '🔇 Audio FX';
        }
    });
}

function startEngineSound() {
    if (!audioCtx) return;
    engineGainNode = audioCtx.createGain();
    engineGainNode.gain.setValueAtTime(0.12, audioCtx.currentTime);

    engineOsc = audioCtx.createOscillator();
    engineOsc.type = 'sawtooth';
    engineOsc.frequency.setValueAtTime(115, audioCtx.currentTime);

    const filter = audioCtx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.setValueAtTime(480, audioCtx.currentTime);

    engineOsc.connect(filter);
    filter.connect(engineGainNode);
    engineGainNode.connect(audioCtx.destination);
    engineOsc.start();
}

function playLaserSound() {
    if (!audioCtx || !audioEnabled) return;
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(920, audioCtx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(140, audioCtx.currentTime + 0.18);

    gain.gain.setValueAtTime(0.24, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.18);

    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start();
    osc.stop(audioCtx.currentTime + 0.19);
}

function playManeuverWhoosh(boost = false) {
    if (!audioCtx || !audioEnabled) return;
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = 'triangle';
    osc.frequency.setValueAtTime(boost ? 380 : 240, audioCtx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(80, audioCtx.currentTime + 0.65);

    gain.gain.setValueAtTime(0.32, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.65);

    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start();
    osc.stop(audioCtx.currentTime + 0.7);
}

// -------------------------------------------------------------
// WEAPONS
// -------------------------------------------------------------
function fireLasers() {
    if (!spaceshipGroup) return;
    playLaserSound();

    const forward = new THREE.Vector3(0, 0, -1).applyEuler(spaceshipGroup.rotation).normalize();
    const right = new THREE.Vector3(1, 0, 0).applyEuler(spaceshipGroup.rotation).normalize();

    [-1.1, 1.1].forEach(offset => {
        const spawnPos = spaceshipGroup.position.clone()
            .add(right.clone().multiplyScalar(offset))
            .add(forward.clone().multiplyScalar(7));

        const boltGeo = new THREE.CylinderGeometry(0.22, 0.22, 14, 5);
        boltGeo.rotateX(Math.PI / 2);
        const boltMat = new THREE.MeshBasicMaterial({ color: 0x38bdf8 });
        const bolt = new THREE.Mesh(boltGeo, boltMat);
        bolt.position.copy(spawnPos);
        bolt.quaternion.copy(spaceshipGroup.quaternion);

        projectileGroup.add(bolt);
        projectiles.push({
            mesh: bolt,
            vel: forward.clone().multiplyScalar(950),
            life: 1.3
        });
    });

    triggerCameraShake(0.3);
}

function spawnExplosion(pos) {
    const pGeo = new THREE.SphereGeometry(1.4, 5, 5);
    const pMat = new THREE.MeshBasicMaterial({ color: 0x38bdf8, transparent: true, opacity: 1 });
    for (let i = 0; i < 14; i++) {
        const mesh = new THREE.Mesh(pGeo, pMat.clone());
        mesh.position.copy(pos);
        const vel = new THREE.Vector3(
            (Math.random() - 0.5) * 70,
            (Math.random() - 0.5) * 70,
            (Math.random() - 0.5) * 70
        );
        explosionGroup.add(mesh);
        explosions.push({ mesh, vel, life: 0.75, maxLife: 0.75 });
    }
}

// -------------------------------------------------------------
// COMBAT MANEUVERS & AERODYNAMICS
// -------------------------------------------------------------
function triggerManeuver(name) {
    flightState.activeManeuver = name;
    flightState.maneuverTime = 0;
    playManeuverWhoosh(true);

    const banner = document.getElementById('notification-banner');
    const titles = {
        'slalom': '⚡ SLALOM CANYON AD ALTA VELOCITÀ',
        'barrelroll': '🔄 BARREL ROLL EVASIVO (DOGFIGHT)',
        'cobra': '🐍 MANOVRA COBRA (VETTORE D\'ATTACCO 90°)',
        'splits': '⬇️ SPLIT-S DIVE (PICCHIATA TATTICA)',
        'salvo': '💥 RAFFICA CANNONI AL PLASMA'
    };
    banner.textContent = titles[name] || 'MANOVRA ATTIVATA';
    banner.style.opacity = '1';
    setTimeout(() => { banner.style.opacity = '0'; }, 2200);

    if (name === 'salvo') {
        for (let k = 0; k < 6; k++) {
            setTimeout(fireLasers, k * 120);
        }
    }
}

function updateFlightPhysics(delta) {
    const t = clock.getElapsedTime();

    if (flightState.mode === 'cinematic') {
        if (!flightState.activeManeuver) {
            flightState.pos.z -= flightState.speed * delta;
            if (flightState.pos.z < -3200) flightState.pos.z = 3000;

            const canyonX = getCanyonCenterX(flightState.pos.z);
            const canyonY = getCanyonCenterY(flightState.pos.z);

            const nextCanyonX = getCanyonCenterX(flightState.pos.z - 80);
            const curveDeltaX = nextCanyonX - canyonX;
            const rollTarget = THREE.MathUtils.clamp(-curveDeltaX * 0.08, -1.3, 1.3);
            const pitchTarget = THREE.MathUtils.clamp((canyonY - flightState.pos.y) * 0.015, -0.6, 0.6);

            flightState.roll = THREE.MathUtils.lerp(flightState.roll, rollTarget, delta * 4.5);
            flightState.pitch = THREE.MathUtils.lerp(flightState.pitch, pitchTarget, delta * 4.0);
            flightState.yaw = THREE.MathUtils.lerp(flightState.yaw, curveDeltaX * 0.03, delta * 3.5);

            flightState.pos.x = THREE.MathUtils.lerp(flightState.pos.x, canyonX, delta * 3.0);
            flightState.pos.y = THREE.MathUtils.lerp(flightState.pos.y, canyonY, delta * 3.0);

            if (Math.random() < 0.018) {
                fireLasers();
            }
        }
    } else {
        let pitchInput = 0, rollInput = 0, yawInput = 0;
        if (inputState.pitchUp) pitchInput += 1;
        if (inputState.pitchDown) pitchInput -= 1;
        if (inputState.rollLeft) rollInput += 1;
        if (inputState.rollRight) rollInput -= 1;
        if (inputState.yawLeft) yawInput += 1;
        if (inputState.yawRight) yawInput += 1;

        pitchInput += inputState.touchY;
        rollInput += inputState.touchX;

        const turnSpeed = 2.6 * delta;
        flightState.pitch += pitchInput * turnSpeed;
        flightState.roll += rollInput * turnSpeed * 1.6;
        flightState.yaw += yawInput * turnSpeed;

        const currentSpeed = inputState.boost ? flightState.maxSpeed : flightState.speed;
        const forward = new THREE.Vector3(0, 0, -1).applyEuler(new THREE.Euler(flightState.pitch, flightState.yaw, flightState.roll, 'YXZ'));
        flightState.pos.add(forward.multiplyScalar(currentSpeed * delta));

        if (inputState.fire) {
            fireLasers();
            inputState.fire = false;
        }
    }

    if (flightState.activeManeuver) {
        flightState.maneuverTime += delta;
        const mTime = flightState.maneuverTime;
        flightState.pos.z -= 280 * delta;

        if (flightState.activeManeuver === 'slalom') {
            const slalomPhase = mTime * 4.2;
            flightState.roll = Math.sin(slalomPhase) * 1.35;
            flightState.pos.x += Math.cos(slalomPhase) * 90 * delta;
            flightState.gForce = 5.0;
            if (mTime > 3.6) flightState.activeManeuver = null;
        } 
        else if (flightState.activeManeuver === 'barrelroll') {
            const rollProgress = (mTime / 1.35) * Math.PI * 2;
            flightState.roll = rollProgress;
            flightState.pos.x += Math.sin(rollProgress) * 35 * delta;
            flightState.pos.y += Math.cos(rollProgress) * 25 * delta;
            flightState.gForce = 6.2;
            if (mTime > 1.35) flightState.activeManeuver = null;
        } 
        else if (flightState.activeManeuver === 'cobra') {
            if (mTime < 0.65) {
                flightState.pitch = THREE.MathUtils.lerp(flightState.pitch, 1.48, delta * 9.5);
                flightState.pos.y += 50 * delta;
                flightState.gForce = 8.4;
            } else if (mTime < 1.4) {
                flightState.pitch = 1.45;
                if (Math.random() < 0.3) fireLasers();
            } else if (mTime < 2.2) {
                flightState.pitch = THREE.MathUtils.lerp(flightState.pitch, 0, delta * 6.5);
            } else {
                flightState.activeManeuver = null;
            }
        }
        else if (flightState.activeManeuver === 'splits') {
            if (mTime < 0.7) {
                flightState.roll = THREE.MathUtils.lerp(flightState.roll, Math.PI, delta * 7.5);
            } else if (mTime < 2.0) {
                flightState.pitch = THREE.MathUtils.lerp(flightState.pitch, -1.15, delta * 5.5);
                flightState.pos.y -= 100 * delta;
                flightState.gForce = 5.6;
            } else if (mTime < 2.8) {
                flightState.roll = THREE.MathUtils.lerp(flightState.roll, 0, delta * 6.5);
                flightState.pitch = THREE.MathUtils.lerp(flightState.pitch, 0, delta * 5.5);
            } else {
                flightState.activeManeuver = null;
            }
        }
    } else {
        flightState.gForce = THREE.MathUtils.lerp(flightState.gForce, 1.0 + Math.abs(flightState.roll) * 2.2, delta * 3.5);
    }

    spaceshipGroup.position.copy(flightState.pos);
    spaceshipGroup.rotation.set(flightState.pitch, flightState.yaw, flightState.roll, 'YXZ');

    // Dynamic Deflection of Control Surfaces
    if (upperRightFinMesh && upperLeftFinMesh && lowerRightFinMesh && lowerLeftFinMesh) {
        const pitchDeflection = flightState.pitch * 0.35;
        const rollDeflection = flightState.roll * 0.25;

        upperRightFinMesh.rotation.y = pitchDeflection - rollDeflection;
        upperLeftFinMesh.rotation.y = pitchDeflection + rollDeflection;
        lowerRightFinMesh.rotation.y = -pitchDeflection - rollDeflection;
        lowerLeftFinMesh.rotation.y = -pitchDeflection + rollDeflection;
    }

    // Ace Combat 7 Style Transonic Vapor Cone during High-G turns or Boost
    if (vaporConeMesh) {
        const targetVaporOpacity = (flightState.gForce > 4.5 || inputState.boost) ? 0.35 : 0.0;
        vaporConeMesh.material.opacity = THREE.MathUtils.lerp(vaporConeMesh.material.opacity, targetVaporOpacity, delta * 8.0);
    }

    // Dynamic Thruster Flame & Shock Diamonds
    const isBoost = inputState.boost || flightState.activeManeuver !== null;
    const flameScaleZ = isBoost ? 1.9 + Math.random() * 0.35 : 1.0 + Math.random() * 0.2;
    thrusterMesh.scale.set(1.0, 1.0, flameScaleZ);
    flameCore.scale.set(1.0, 1.0, flameScaleZ * 1.1);
    thrusterLight.intensity = isBoost ? 6.8 : 3.8;

    flameDiamonds.forEach((dia) => {
        dia.scale.setScalar(isBoost ? 1.4 : 1.0);
        dia.rotation.z += 0.1;
    });

    spawnThrusterParticles();
    spawnWingtipVortices();
    updateTelemetry();
}

// Ace Combat 7 Wingtip Vortex Trails
function spawnWingtipVortices() {
    if (flightState.gForce < 2.5 && !inputState.boost) return;
    [-3.2, 3.2].forEach(offset => {
        const pos = spaceshipGroup.position.clone()
            .add(new THREE.Vector3(offset, 0.1, 4.0).applyEuler(spaceshipGroup.rotation));

        const pGeo = new THREE.SphereGeometry(0.24, 4, 4);
        const pMat = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.45 });
        const p = new THREE.Mesh(pGeo, pMat);
        p.position.copy(pos);
        particleGroup.add(p);

        thrusterParticles.push({
            mesh: p,
            vel: new THREE.Vector3(0, 0, 30).applyEuler(spaceshipGroup.rotation),
            life: 0.4,
            maxLife: 0.4
        });
    });
}

function spawnThrusterParticles() {
    if (!spaceshipGroup) return;
    const rearPos = spaceshipGroup.position.clone()
        .add(new THREE.Vector3(0, 0.1, 10.8).applyEuler(spaceshipGroup.rotation));

    const pGeo = new THREE.SphereGeometry(0.32, 4, 4);
    const pMat = new THREE.MeshBasicMaterial({
        color: 0x38bdf8,
        transparent: true,
        opacity: 0.8
    });
    const pMesh = new THREE.Mesh(pGeo, pMat);
    pMesh.position.copy(rearPos).add(new THREE.Vector3(
        (Math.random() - 0.5) * 0.5,
        (Math.random() - 0.5) * 0.5,
        (Math.random() - 0.5) * 0.5
    ));
    particleGroup.add(pMesh);

    thrusterParticles.push({
        mesh: pMesh,
        vel: new THREE.Vector3(0, 0, 95).applyEuler(spaceshipGroup.rotation),
        life: 0.30,
        maxLife: 0.30
    });
}

function updateParticles(delta) {
    for (let i = thrusterParticles.length - 1; i >= 0; i--) {
        const p = thrusterParticles[i];
        p.life -= delta;
        p.mesh.position.addScaledVector(p.vel, delta);
        p.mesh.scale.multiplyScalar(0.92);
        p.mesh.material.opacity = p.life / p.maxLife;

        if (p.life <= 0) {
            particleGroup.remove(p.mesh);
            p.mesh.geometry.dispose();
            p.mesh.material.dispose();
            thrusterParticles.splice(i, 1);
        }
    }

    for (let i = projectiles.length - 1; i >= 0; i--) {
        const proj = projectiles[i];
        proj.life -= delta;
        proj.mesh.position.addScaledVector(proj.vel, delta);

        if (proj.life <= 0) {
            spawnExplosion(proj.mesh.position);
            projectileGroup.remove(proj.mesh);
            proj.mesh.geometry.dispose();
            proj.mesh.material.dispose();
            projectiles.splice(i, 1);
        }
    }

    for (let i = explosions.length - 1; i >= 0; i--) {
        const exp = explosions[i];
        exp.life -= delta;
        exp.mesh.position.addScaledVector(exp.vel, delta);
        exp.mesh.material.opacity = exp.life / exp.maxLife;

        if (exp.life <= 0) {
            explosionGroup.remove(exp.mesh);
            exp.mesh.geometry.dispose();
            exp.mesh.material.dispose();
            explosions.splice(i, 1);
        }
    }
}

function triggerCameraShake(amount) {
    cameraShakeAmount = amount;
}

let cameraShakeAmount = 0;
function updateCamera(delta) {
    if (flightState.camMode === 'free') {
        controls.target.copy(spaceshipGroup.position);
        controls.update();
        return;
    }

    let targetCamPos = new THREE.Vector3();
    let lookTarget = spaceshipGroup.position.clone();

    if (flightState.camMode === 'action') {
        const offset = new THREE.Vector3(0, 5.8, 38).applyEuler(new THREE.Euler(0, flightState.yaw, 0));
        targetCamPos.copy(spaceshipGroup.position).add(offset);
        lookTarget.add(new THREE.Vector3(0, 0, -45).applyEuler(spaceshipGroup.rotation));
        camera.position.lerp(targetCamPos, delta * 6.5);
        camera.lookAt(lookTarget);
    } 
    else if (flightState.camMode === 'cockpit') {
        const cockpitOffset = new THREE.Vector3(0, 0.75, -2.0).applyEuler(spaceshipGroup.rotation);
        targetCamPos.copy(spaceshipGroup.position).add(cockpitOffset);
        lookTarget.copy(targetCamPos).add(new THREE.Vector3(0, 0, -100).applyEuler(spaceshipGroup.rotation));
        camera.position.copy(targetCamPos);
        camera.lookAt(lookTarget);
    }
    else if (flightState.camMode === 'flyby') {
        if (camera.position.distanceTo(spaceshipGroup.position) > 420 || camera.position.y < 100) {
            flightState.currentFlybyPos.set(
                spaceshipGroup.position.x + (Math.random() - 0.5) * 140,
                spaceshipGroup.position.y + (Math.random() - 0.5) * 70,
                spaceshipGroup.position.z - 260
            );
            camera.position.copy(flightState.currentFlybyPos);
        }
        camera.lookAt(spaceshipGroup.position);
    }

    if (cameraShakeAmount > 0) {
        camera.position.x += (Math.random() - 0.5) * cameraShakeAmount;
        camera.position.y += (Math.random() - 0.5) * cameraShakeAmount;
        cameraShakeAmount = Math.max(0, cameraShakeAmount - delta * 2.0);
    }
}

function updateTelemetry() {
    const speedMach = (flightState.speed / 60).toFixed(1);
    document.getElementById('val-speed').textContent = `Mach ${speedMach}`;
    document.getElementById('val-gforce').textContent = `${flightState.gForce.toFixed(1)} G`;
    document.getElementById('val-alt').textContent = `${Math.round(flightState.pos.y)} m`;

    const gMeterFill = document.getElementById('g-force-fill');
    const gPct = Math.min(100, (flightState.gForce / 9.0) * 100);
    gMeterFill.style.height = `${gPct}%`;
    gMeterFill.style.backgroundColor = flightState.gForce > 5.0 ? '#ef4444' : (flightState.gForce > 3.0 ? '#f59e0b' : '#38bdf8');
    document.getElementById('g-label-text').textContent = `${flightState.gForce.toFixed(1)} G`;
}

function setupEventListeners() {
    const btnCinematic = document.getElementById('btn-mode-cinematic');
    const btnManual = document.getElementById('btn-mode-manual');

    btnCinematic.addEventListener('click', () => {
        flightState.mode = 'cinematic';
        btnCinematic.classList.add('active');
        btnManual.classList.remove('active');
    });

    btnManual.addEventListener('click', () => {
        flightState.mode = 'manual';
        btnManual.classList.add('active');
        btnCinematic.classList.remove('active');
    });

    document.getElementById('btn-maneuver-slalom').addEventListener('click', () => triggerManeuver('slalom'));
    document.getElementById('btn-maneuver-barrelroll').addEventListener('click', () => triggerManeuver('barrelroll'));
    document.getElementById('btn-maneuver-cobra').addEventListener('click', () => triggerManeuver('cobra'));
    document.getElementById('btn-maneuver-splits').addEventListener('click', () => triggerManeuver('splits'));
    document.getElementById('btn-fire-salvo').addEventListener('click', () => triggerManeuver('salvo'));

    const camButtons = {
        'btn-cam-action': 'action',
        'btn-cam-cockpit': 'cockpit',
        'btn-cam-flyby': 'flyby',
        'btn-cam-free': 'free'
    };

    Object.keys(camButtons).forEach(id => {
        document.getElementById(id).addEventListener('click', (e) => {
            Object.keys(camButtons).forEach(k => document.getElementById(k).classList.remove('active'));
            e.target.classList.add('active');
            flightState.camMode = camButtons[id];
            controls.enabled = (flightState.camMode === 'free');
        });
    });

    window.addEventListener('keydown', (e) => {
        if (e.code === 'KeyW' || e.code === 'ArrowUp') inputState.pitchDown = true;
        if (e.code === 'KeyS' || e.code === 'ArrowDown') inputState.pitchUp = true;
        if (e.code === 'KeyA' || e.code === 'ArrowLeft') inputState.rollLeft = true;
        if (e.code === 'KeyD' || e.code === 'ArrowRight') inputState.rollRight = true;
        if (e.code === 'KeyQ') inputState.yawLeft = true;
        if (e.code === 'KeyE') inputState.yawRight = true;
        if (e.code === 'ShiftLeft' || e.code === 'ShiftRight') inputState.boost = true;
        if (e.code === 'Space') fireLasers();
        if (e.code === 'Digit1') triggerManeuver('slalom');
        if (e.code === 'Digit2') triggerManeuver('barrelroll');
        if (e.code === 'Digit3') triggerManeuver('cobra');
    });

    window.addEventListener('keyup', (e) => {
        if (e.code === 'KeyW' || e.code === 'ArrowUp') inputState.pitchDown = false;
        if (e.code === 'KeyS' || e.code === 'ArrowDown') inputState.pitchUp = false;
        if (e.code === 'KeyA' || e.code === 'ArrowLeft') inputState.rollLeft = false;
        if (e.code === 'KeyD' || e.code === 'ArrowRight') inputState.rollRight = false;
        if (e.code === 'KeyQ') inputState.yawLeft = false;
        if (e.code === 'KeyE') inputState.yawRight = false;
        if (e.code === 'ShiftLeft' || e.code === 'ShiftRight') inputState.boost = false;
    });

    document.getElementById('btn-record-video').addEventListener('click', toggleVideoRecording);
}

function setupMobileTouch() {
    const touchStick = document.getElementById('touch-stick');
    const touchThumb = document.getElementById('touch-thumb');
    let touchOrigin = { x: 0, y: 0 };
    let isTouching = false;

    touchStick.addEventListener('touchstart', (e) => {
        isTouching = true;
        const rect = touchStick.getBoundingClientRect();
        touchOrigin = { x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 };
        handleTouchMove(e);
    });

    touchStick.addEventListener('touchmove', (e) => {
        if (!isTouching) return;
        handleTouchMove(e);
    });

    const resetTouch = () => {
        isTouching = false;
        inputState.touchX = 0;
        inputState.touchY = 0;
        touchThumb.style.transform = 'translate(-50%, -50%)';
    };

    touchStick.addEventListener('touchend', resetTouch);
    touchStick.addEventListener('touchcancel', resetTouch);

    function handleTouchMove(e) {
        const touch = e.touches[0];
        const dx = touch.clientX - touchOrigin.x;
        const dy = touch.clientY - touchOrigin.y;
        const maxDist = 45;
        const dist = Math.min(maxDist, Math.hypot(dx, dy));
        const angle = Math.atan2(dy, dx);

        const thumbX = Math.cos(angle) * dist;
        const thumbY = Math.sin(angle) * dist;
        touchThumb.style.transform = `translate(calc(-50% + ${thumbX}px), calc(-50% + ${thumbY}px))`;

        inputState.touchX = thumbX / maxDist;
        inputState.touchY = -thumbY / maxDist;
    }

    const fireBtn = document.getElementById('mobile-fire-btn');
    fireBtn.addEventListener('touchstart', (e) => { e.preventDefault(); fireLasers(); });

    const boostBtn = document.getElementById('mobile-boost-btn');
    boostBtn.addEventListener('touchstart', (e) => { e.preventDefault(); inputState.boost = true; });
    boostBtn.addEventListener('touchend', () => { inputState.boost = false; });
}

function toggleVideoRecording() {
    const btnRecord = document.getElementById('btn-record-video');

    if (!isRecording) {
        const stream = renderer.domElement.captureStream(60);
        let mimeType = 'video/webm;codecs=vp9';
        if (!MediaRecorder.isTypeSupported(mimeType)) {
            mimeType = 'video/webm';
        }

        recordedChunks = [];
        mediaRecorder = new MediaRecorder(stream, { mimeType, videoBitsPerSecond: 10000000 });

        mediaRecorder.ondataavailable = (e) => {
            if (e.data.size > 0) recordedChunks.push(e.data);
        };

        mediaRecorder.onstop = () => {
            const blob = new Blob(recordedChunks, { type: mimeType });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `JATUA_Dark_TripleA_Combat_${Date.now()}.webm`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            setTimeout(() => URL.revokeObjectURL(url), 2000);
        };

        mediaRecorder.start();
        isRecording = true;
        btnRecord.classList.add('active');
        btnRecord.textContent = '⏹️ Termina & Scarica Video';
    } else {
        mediaRecorder.stop();
        isRecording = false;
        btnRecord.classList.remove('active');
        btnRecord.textContent = '🔴 Registra Video MP4';
    }
}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

function animate() {
    requestAnimationFrame(animate);
    const delta = Math.min(clock.getDelta(), 0.1);

    updateFlightPhysics(delta);
    updateTraffic(delta);
    updateSkyTrains(delta);
    updateSteam(delta);
    updateParticles(delta);
    updateCamera(delta);

    renderer.render(scene, camera);
}
