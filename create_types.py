#!/usr/bin/python3
from collections import OrderedDict
import html
import json
import os
import clipboard

DIR = 'cpp'
# %USERPROFILE%\AppData\Roaming\Code\User\snippets
VSCODE_JSON_INPUT_PATH = (os.environ['USERPROFILE'] + '/AppData/Roaming/Code/User/snippets/cpp.json').replace('\\','/')
VSCODE_JSON_OUTPUT_PATH = r'cpp.json'

def is_comment(s):
    return s.strip().startswith('//')


class Literal:
    def __init__(self, id: str, default: str, tooltip=None):
        self.id = id
        self.default = default
        self.tooltip = tooltip if tooltip else id.capitalize()


class VsCodeSnippet:
    def __init__(self, body):
        self.body = [body] if isinstance(body, str) else body


class Snippet:
    def __init__(self, title: str, shortcut: str, code=None, description=None, *, literals=None, vscode: VsCodeSnippet = None):
        assert(title)
        assert(shortcut)
        self.title = title
        self.shortcut = shortcut
        self.description = description if description is not None else title
        self.code = code if code is not None else ''
        self.literals = literals if literals is not None else []
        self.vscode = vscode

    def declarations_xml(self):
        if not self.literals:
            return ''
        indent = ' ' * 4
        lines = ['', f'{indent*3}<Declarations>']
        for literal in self.literals:
            lines.append(f'{indent*4}<Literal>')
            lines.append(f'{indent*5}<ID>{literal.id}</ID>')
            lines.append(f'{indent*5}<Default>{literal.default}</Default>')
            lines.append(f'{indent*5}<ToolTip>{literal.tooltip}</ToolTip>')
            lines.append(f'{indent*4}</Literal>')
        lines.append(f'{indent*3}</Declarations>')
        return '\n'.join(lines)

    def xml_str(self):
        # Make sure there is no line break before </Code>
        return f'''
<?xml version="1.0" encoding="utf-8"?>
<CodeSnippets xmlns="http://schemas.microsoft.com/VisualStudio/2005/CodeSnippet">
    <CodeSnippet Format="1.0.0">
        <Header>
            <Title>{self.title}</Title>
            <Description>{html.escape(self.description)}</Description>
            <Shortcut>{self.shortcut}</Shortcut>
        </Header>
        <Snippet>{self.declarations_xml()}
            <Code Language="CPP"><![CDATA[{self.code}]]></Code>
        </Snippet>
    </CodeSnippet>
</CodeSnippets>
'''

    def vscode_json(self):
        obj = {}
        if self.vscode:
            obj['prefix'] = self.shortcut
            obj['description'] = self.description
            obj['body'] = self.vscode.body
        return obj


def gen_vscode_json(snippets):
    comments_lines, json_lines = [], []
    with open(VSCODE_JSON_INPUT_PATH) as f:
        for line in f:
            if is_comment(line):
                comments_lines.append(line)
            else:
                json_lines.append(line)
    objects = json.loads(''.join(json_lines))
    # objects = {}
    for sn in snippets:
        objects[sn.title] = sn.vscode_json()
    json_text = json.dumps(objects, indent=4, sort_keys=False)
    assert json_text.startswith('{\n')
    json_text = json_text[2:]
    json_text = '{\n' + ''.join(comments_lines) + json_text
    return json_text


def write_to_file(filename, text):
    with open(filename, 'w') as fp:
        fp.write(text)


def main():
    types = OrderedDict([
        ('u8', 'uint8_t'),
        ('u16', 'uint16_t'),
        ('u32', 'uint32_t'),
        ('u64', 'uint64_t'),
        ('i8', 'int8_t'),
        ('i16', 'int16_t'),
        ('i32', 'int32_t'),
        ('i64', 'int64_t'),
        ('size_t', 'size_t'),
        ('str', 'std::string'),
        ('wstr', 'std::wstring'),
        ('nullptr', 'nullptr'),
        ('nano', 'std::chrono::nanoseconds'),
    ])
    # for shortcut, typename in types.items():
    #     filename = os.path.join(DIR, f'{shortcut}.snippet')
    #     with open(filename, 'w') as fp:
    #         fp.write(type_text(shortcut, typename))

    ExpressionLiteral = Literal('expression', '/*expression*/')
    TypeLiteral = Literal('type', '/*type*/')

    snippets = []
    snippets.append(Snippet(title='std::move',
                            shortcut='move',
                            description='std::move(expression)',
                            code='std::move($expression$)$end$',
                            literals=[ExpressionLiteral],
                            vscode=VsCodeSnippet(
                                r'std::move(${1:/*expression*/})$0')
                            ))
    snippets.append(Snippet(title='std::shared_ptr',
                            shortcut='shared',
                            description='std::shared_ptr<type>',
                            code='std::shared_ptr<$selected$>$end$',
                            literals=[TypeLiteral],
                            vscode=VsCodeSnippet(
                                r'std::shared_ptr<${1:/*type*/}>$0')
                            ))
    snippets.append(Snippet(title='std::unique_ptr',
                            shortcut='unique',
                            description='std::unique_ptr<type>',
                            code='std::unique_ptr<$selected$>$end$',
                            literals=[TypeLiteral],
                            vscode=VsCodeSnippet(
                                r'std::unique_ptr<${1:/*type*/}>$0')
                            ))
    snippets.append(Snippet(title='static_cast',
                            shortcut='sc',
                            description='static_cast<type>(expression)',
                            code='static_cast($expression$)$end$',
                            literals=[Literal('type', 'uint32_t'),
                                      ExpressionLiteral],
                            vscode=VsCodeSnippet(
                                r'static_cast<${1:uint32_t}>(${2:/*expression*/})$0')
                            ))
    snippets.append(Snippet(title='std::vector',
                            shortcut='vector',
                            description='std::vector<type>',
                            code='std::unordered_map<$type$>$end$',
                            literals=[Literal('type', '/*type*/')],
                            vscode=VsCodeSnippet(
                                r'std::vector<${1:/*type*/}>$0')
                            ))
    snippets.append(Snippet(title='std::unordered_map',
                            shortcut='umap',
                            description='std::unordered_map<key, value>',
                            code='std::unordered_map<$key$, $value$>$end$',
                            literals=[Literal('key', '/*key*/'),
                                      Literal('value', '/*value*/')],
                            vscode=VsCodeSnippet(
                                r'std::unordered_map<${1:/*key*/}, ${2:/*value*/}>$0')
                            ))
    snippets.append(Snippet(title='XR_NULL_HANDLE',
                            shortcut='xrnull',
                            description='XR_NULL_HANDLE',
                            code='XR_NULL_HANDLE$end$',
                            vscode=VsCodeSnippet('XR_NULL_HANDLE')
                            ))

    output = []

    for shortcut, typename in types.items():
        sn = Snippet(shortcut, shortcut,
                     code=f'{typename} $end$', description=typename, vscode=VsCodeSnippet(body=typename))
        snippets.append(sn)

    for sn in snippets:
        output.append(sn.xml_str())

    json_text = gen_vscode_json(snippets)
    write_to_file(VSCODE_JSON_OUTPUT_PATH, json_text)

    output.append(json_text)
    text = '\n'.join(output)
    clipboard.copy(text)
    for line in output:
        print(line)


if __name__ == '__main__':
    main()
