# Read Me!

#### setup.py
```
from setuptools import setup
setup()
```

#### dev
```
$ pip install -e .[dev]
```

macのzsh

```
% pip install -e '.[dev]'
```

zsh: no matches found: .[dev]のエラーは、zshが.[dev]というパターンを展開しようとして失敗していることを示しています。