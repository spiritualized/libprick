# libprick

Generate metadata-independent sha256 hashes of audio/video streams. Useful for deduplicating retagged music files.

```python
from libprick import Pricker

pricker = Pricker()

pricker.open('/path/to/file.mp3')

print(pricker.hexdigest())
```