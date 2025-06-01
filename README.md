# Traktor-NML-to-Rekordbox-XML

Python script to convert your Traktor playlists to Rekordbox XML. It keeps:

- [x] Hot Cues (with names)
- [x] Saved loops (with names)
- [x] Track color
- [x] Playtime
- [x] Genre / Artist / Title / Music tonality / etc.
- [x] Pad order of Hots Cues and Loops
- [x] Flexible beatgrid
- [x] Rekordbox XML <=> Traktor NML

### To be added

- [ ] Playlist tree-structure
- [ ] Web interface to load file
- [ ] Custom loop length for Traktor

## How to

### Traktor to Rekordbox
1. Export your playlist in Traktor in NML (Right-click on the playlist > Export Playlist > NML)
2. `python nml_to_rekord.py <path/to/your/playlist>.nml`
3. Open Rekordbox > Preferences > View > Layout > Tree View > Check rekordbox xml
4. Preferences > Advanced > Database > rekordbox xml > Imported Library > Select `<outputed_playlist>.rekordbox.xml`
5. In the sidebar of Rekordbox should appear a `rekordbox xml` section > All tracks
6. Tada! 🎉

### Rekordbox to Traktor
1. In Rekordbox, export your collection: File > Export Collection in xml format > Pick any location
2. `python rekord_to_nml.py <path/to/your/collection>.xml`
3. Open Traktor > Right-click on the Playlists > Import Playlist > Choose the `<outputed_collection>.nml` file
4. Tada! 🥳

## Links
- [Traktor NML utils library](https://pypi.org/project/traktor-nml-utils/)
- [Rekordbox XML schema](https://cdn.rekordbox.com/files/20200410160904/xml_format_list.pdf)
- [TraktorBox library](https://github.com/nonodesbois42/TraktorBox/tree/main)
