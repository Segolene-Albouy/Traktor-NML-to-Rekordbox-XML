# Traktor-NML-to-Rekordbox-XML

Python script to convert your Traktor playlists to Rekordbox XML (with Hot Cues and Loops)

## How to

1. Export your playlist in Traktor in NML
2. `python nml_to_rekord.py <path/to/your/playlist.nml`
3. Open Rekordbox > Preferences > View > Layout > Tree View > Check rekordbox xml
4. Preferences > Advanced > Database > rekorbox xml > Imported Library > Select `outputed_playlist.rekordbox.xml`
5. In the sidebar of Rekordbox should appear a `rekordbox xml` section > All tracks
6. Tada!
