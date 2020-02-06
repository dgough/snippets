#!/usr/bin/python3

from collections import namedtuple
import os

AUTHOR = 'Darryl Gough'
DIR = 'cpp'

def type_text(shortcut, typename):
    return f'''<?xml version="1.0" encoding="utf-8"?>
<CodeSnippets xmlns="http://schemas.microsoft.com/VisualStudio/2005/CodeSnippet">
    <CodeSnippet Format="1.0.0">
        <Header>
            <Title>{shortcut}</Title>
            <Author>{AUTHOR}</Author>
            <Description>{typename}</Description>
            <Shortcut>{shortcut}</Shortcut>
        </Header>
        <Snippet>
            <Code Language="CPP">
                <![CDATA[{typename} $end$]]>
            </Code>
        </Snippet>
    </CodeSnippet>
</CodeSnippets>
'''

def main():
    types = {
        "u8"   : "uint8_t",
        "u16"  : "uint16_t",
        "u32"  : "uint32_t",
        "u64"  : "uint64_t",
        "i8"   : "int8_t",
        "i16"  : "int16_t",
        "i32"  : "int32_t",
        "i64"  : "int64_t",
        "size" : "size_t",
        "str"  : "std::string",
        "wstr" : "std::wstring",
    }
    for shortcut, typename in types.items():
        filename = os.path.join(DIR, f'{shortcut}.snippet')
        with open(filename, 'w') as fp:
            fp.write(type_text(shortcut, typename))


if __name__ == '__main__':
    main()
