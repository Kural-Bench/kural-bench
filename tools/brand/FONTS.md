# Brand fonts

IBM Plex Sans and IBM Plex Mono are used as designed. The Tamil face is Noto Sans Tamil, not IBM Plex Sans Tamil:
the release assets of github.com/IBM/plex that were reachable when the figures were built contain no Tamil package
(`@ibm/plex-sans-tamil` has no release asset there), so Noto Sans Tamil v2.004 from github.com/notofonts/tamil, also
SIL OFL 1.1, stands in. To switch, change the Tamil entries in `FACES` (`tools/brand/glyphs.py`) and in `SPEC`
(`tools/brand/fonts.py`).

| Family | Version | Licence |
|---|---|---|
| IBM Plex Sans | `@ibm/plex-sans@1.1.0` | SIL OFL 1.1 |
| IBM Plex Mono | `@ibm/plex-mono@1.1.0` | SIL OFL 1.1 |
| Noto Sans Tamil | `NotoSansTamil-v2.004` | SIL OFL 1.1 |

`tools/brand/build.py` downloads the files below into `tools/brand/fonts/` (git-ignored) and checks both sha256 values.
The glyphs are outlined into the SVG files, so the fonts are not needed to view the figures.

| File | URL of the archive | Member | sha256 of the archive | sha256 of the file |
|---|---|---|---|---|
| `IBMPlexSans-Regular.ttf` | https://github.com/IBM/plex/releases/download/%40ibm%2Fplex-sans%401.1.0/ibm-plex-sans.zip | `ibm-plex-sans/fonts/complete/ttf/IBMPlexSans-Regular.ttf` | `fb365d910566e6d199cc2c15579a7dd9a267128e18431a394ed81f1970c69200` | `975dcda37d80f038dcd143c22e33ca2d97a0cc5a929aace1c749153b0fe1afa5` |
| `IBMPlexSans-Medium.ttf` | https://github.com/IBM/plex/releases/download/%40ibm%2Fplex-sans%401.1.0/ibm-plex-sans.zip | `ibm-plex-sans/fonts/complete/ttf/IBMPlexSans-Medium.ttf` | `fb365d910566e6d199cc2c15579a7dd9a267128e18431a394ed81f1970c69200` | `331c8639d7598b2cde62a911a71db195e30cb655cd6bdf2e324a7e984955f907` |
| `IBMPlexSans-SemiBold.ttf` | https://github.com/IBM/plex/releases/download/%40ibm%2Fplex-sans%401.1.0/ibm-plex-sans.zip | `ibm-plex-sans/fonts/complete/ttf/IBMPlexSans-SemiBold.ttf` | `fb365d910566e6d199cc2c15579a7dd9a267128e18431a394ed81f1970c69200` | `a20caf8286023a6a7a85e40b1d2a4ae9fc3e3b1f9eda8f4c542dd4986af67bb1` |
| `IBMPlexMono-Regular.ttf` | https://github.com/IBM/plex/releases/download/%40ibm%2Fplex-mono%401.1.0/ibm-plex-mono.zip | `ibm-plex-mono/fonts/complete/ttf/IBMPlexMono-Regular.ttf` | `4bfc936d0e1fd19db6327a3786eabdbc3dc0d464500576f6458f6706df68d26c` | `fe11304a5fe956d5744e9b6a246cc83d90425245e75a62230044966ca96a7f50` |
| `NotoSansTamil-Regular.ttf` | https://github.com/notofonts/tamil/releases/download/NotoSansTamil-v2.004/NotoSansTamil-v2.004.zip | `NotoSansTamil/full/ttf/NotoSansTamil-Regular.ttf` | `f8284e0f200a7f29a439b4ec88280d864b2b31f8479111c5b658ba6da38b3005` | `0afbc221964b6048c6d771c525be474d21b288a621dce0fafedd695cc5c98e4e` |
| `NotoSansTamil-Medium.ttf` | https://github.com/notofonts/tamil/releases/download/NotoSansTamil-v2.004/NotoSansTamil-v2.004.zip | `NotoSansTamil/full/ttf/NotoSansTamil-Medium.ttf` | `f8284e0f200a7f29a439b4ec88280d864b2b31f8479111c5b658ba6da38b3005` | `214dd91b9afa434c00cc877ece3e9c188cd6db8661cd7350d13f4d3918e5acaf` |
| `NotoSansTamil-SemiBold.ttf` | https://github.com/notofonts/tamil/releases/download/NotoSansTamil-v2.004/NotoSansTamil-v2.004.zip | `NotoSansTamil/full/ttf/NotoSansTamil-SemiBold.ttf` | `f8284e0f200a7f29a439b4ec88280d864b2b31f8479111c5b658ba6da38b3005` | `5ddb20a37647c0c529e6f751106dac403b9969579ccf4246d8b5d135accb4cc6` |
