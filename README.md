# Traktor-NML-to-Rekordbox-XML

Python script to convert your Traktor playlists to Rekordbox XML. It keeps:

- [x] Hot Cues (with names)
- [x] Saved loops (with names)
- [x] Track color
- [x] Playtime
- [x] Genre / Artist / Title / Music tonality / etc.
- [x] Pad order of Hots Cues and Loops

### To be added

- [ ] Playlist tree-structure
- [ ] Web interface to load file
- [ ] Rekordbox XML => Traktor NML 

## How to

1. Export your playlist in Traktor in NML
2. `python nml_to_rekord.py <path/to/your/playlist>.nml`
3. Open Rekordbox > Preferences > View > Layout > Tree View > Check rekordbox xml
4. Preferences > Advanced > Database > rekorbox xml > Imported Library > Select `<outputed_playlist>.rekordbox.xml`
5. In the sidebar of Rekordbox should appear a `rekordbox xml` section > All tracks
6. Tada!

## Links
- [Traktor NML utils library](https://pypi.org/project/traktor-nml-utils/)
- [Rekordbox XML schema](https://cdn.rekordbox.com/files/20200410160904/xml_format_list.pdf)
- [TraktorBox library](https://github.com/nonodesbois42/TraktorBox/tree/main)
