import re

with open('/root/shift-app/src/App.jsx', 'r') as f:
    content = f.read()

# Fix 1: Restore the loading screen footer
bad_loading = """        </div>
          letterSpacing: '0.1em',
          textTransform: 'uppercase'
        }}>
          Developed by <span style={{ color: 'var(--text-light)', fontWeight: '600' }}>Antpower74</span>
        </footer>
      </div>"""

good_loading = """        </div>
        
        <footer style={{
          textAlign: 'center',
          marginTop: 'auto',
          color: 'var(--text-muted)',
          fontSize: '0.75rem',
          fontWeight: '400',
          letterSpacing: '0.1em',
          textTransform: 'uppercase'
        }}>
          Developed by <span style={{ color: 'var(--text-light)', fontWeight: '600' }}>Antpower74</span>
        </footer>
      </div>"""

content = content.replace(bad_loading, good_loading)

# Fix 2: Close the main content fragment correctly.
# Find where the timeline-container / depot-grid ends before the footer.
# Currently the bottom is:
#         </div>
#       )}
#       
#       {activeTab === 'shifts' && (
#       <footer style={{

# We need to insert `</>)}` before the footer.
bad_bottom = """        </div>
      )}
      
      {activeTab === 'shifts' && (
      <footer style={{"""

good_bottom = """        </div>
      )}
      </>
      )}
      
      <footer style={{"""

content = content.replace(bad_bottom, good_bottom)

# Also remove the `{activeTab === 'shifts' && (` from the footer, it should be visible always!
bad_footer = """      </>
      )}
      
      {activeTab === 'shifts' && (
      <footer style={{"""

good_footer = """      </>
      )}
      
      <footer style={{"""

content = content.replace(bad_footer, good_footer)

bad_footer_end = """      </footer>
      )}
    </div>
  );"""

good_footer_end = """      </footer>
    </div>
  );"""

content = content.replace(bad_footer_end, good_footer_end)

with open('/root/shift-app/src/App.jsx', 'w') as f:
    f.write(content)

print("Fixed App.jsx")
