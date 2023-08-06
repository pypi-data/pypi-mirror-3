#!/usr/bin/env python
import distutils.core

distutils.core.setup(
    name = "simple-jsonrpc",
    version = "0.3.3",
    py_modules = ["simplejsonrpc"],
    author = "Deng Zhiping",
    author_email = "kofreestyler@gmail.com",
    url = "https://github.com/dengzhp/simple-jsonrpc",
    license = "http://www.apache.org/licenses/LICENSE-2.0",
    description = "a simple JSON-RPC v2.0 library",
    long_description = "A python library of JSON-RPC v2.0 specification"
)
