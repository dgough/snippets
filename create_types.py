#!/usr/bin/python3
from collections import OrderedDict
import html
import json
import os
import clipboard
from typing import List

DIR = 'cpp'
# %USERPROFILE%\AppData\Roaming\Code\User\snippets
VSCODE_JSON_INPUT_PATH = (
    os.environ['USERPROFILE'] + '/AppData/Roaming/Code/User/snippets/cpp.json').replace('\\', '/')
VSCODE_JSON_OUTPUT_PATH = r'cpp.json'
SHOULD_UPDATE_VSCODE_JSON_FILE = False


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
        return f'''<?xml version="1.0" encoding="utf-8"?>
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
</CodeSnippets>'''

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


def write_to_file(filename, text: str):
    with open(filename, 'w') as fp:
        fp.write(text)


def snippet_filename(name: str):
    name = name.replace('std::', '').replace('::', '_')
    return name + '.snippet'


def add_new_snippet_files(snippets: List[Snippet]):
    for snippet in snippets:
        filepath = os.path.join(DIR, snippet_filename(snippet.title))
        write_to_file(filepath, snippet.xml_str())
        # if not os.path.exists(filepath):
        #     write_to_file(filepath, snippet.xml_str())


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

    ExpressionLiteral = Literal('expression', 'expression')
    TypeLiteral = Literal('type', 'type')
    SelectedTypeLiteral = Literal('selected', 'type')
    SelectedExpressionLiteral = Literal('selected', 'expression')

    snippets = []
    snippets.append(Snippet(title='move',
                            shortcut='move',
                            description='std::move(expression)',
                            code='std::move($selected$)$end$',
                            literals=[SelectedExpressionLiteral],
                            vscode=VsCodeSnippet(
                                r'std::move(${1:expression})$0')
                            ))
    snippets.append(Snippet(title='shared_ptr',
                            shortcut='shared_ptr',
                            description='std::shared_ptr<type>',
                            code='std::shared_ptr<$selected$>$end$',
                            literals=[SelectedTypeLiteral],
                            vscode=VsCodeSnippet(
                                r'std::shared_ptr<${1:type}>$0')
                            ))
    snippets.append(Snippet(title='unique_ptr',
                            shortcut='unique_ptr',
                            description='std::unique_ptr<type>',
                            code='std::unique_ptr<$selected$>$end$',
                            literals=[SelectedTypeLiteral],
                            vscode=VsCodeSnippet(
                                r'std::unique_ptr<${1:type}>$0')
                            ))
    snippets.append(Snippet(title='make_unique',
                            shortcut='make_unique',
                            description='std::make_unique<type>()',
                            code='std::make_unique<$selected$>($end$)',
                            literals=[SelectedTypeLiteral],
                            vscode=VsCodeSnippet(
                                r'std::make_unique<${1:type}>($0)')
                            ))
    snippets.append(Snippet(title='make_shared',
                            shortcut='make_shared',
                            description='std::make_shared<type>()',
                            code='std::make_shared<$selected$>($end$)',
                            literals=[SelectedTypeLiteral],
                            vscode=VsCodeSnippet(
                                r'std::make_shared<${1:type}>($0)')
                            ))
    snippets.append(Snippet(title='static_cast',
                            shortcut='sc',
                            description='static_cast<type>(expression)',
                            code='static_cast<$type$>($selected$)$end$',
                            literals=[Literal('type', 'uint32_t'),
                                      SelectedExpressionLiteral],
                            vscode=VsCodeSnippet(
                                r'static_cast<${1:uint32_t}>(${2:expression})$0')
                            ))
    snippets.append(Snippet(title='vector',
                            shortcut='vector',
                            description='std::vector<type>',
                            code='std::vector<$selected$>$end$',
                            literals=[SelectedTypeLiteral],
                            vscode=VsCodeSnippet(
                                r'std::vector<${1:type}>$0')
                            ))
    snippets.append(Snippet(title='unordered_map',
                            shortcut='umap',
                            description='std::unordered_map<key, value>',
                            code='std::unordered_map<$key$, $value$>$end$',
                            literals=[Literal('key', 'key'),
                                      Literal('value', 'value')],
                            vscode=VsCodeSnippet(
                                r'std::unordered_map<${1:key}, ${2:value}>$0')
                            ))
    snippets.append(Snippet(title='array',
                            shortcut='array',
                            description='std::array<type, size>',
                            code='std::array<$selected$, $size$>$end$',
                            literals=[Literal('selected', 'type'),
                                      Literal('size', 'size')],
                            vscode=VsCodeSnippet(
                                r'std::array<${1:type}, ${2:size}>$0')
                            ))
    snippets.append(Snippet(title='XR_NULL_HANDLE',
                            shortcut='xrnull',
                            description='XR_NULL_HANDLE',
                            code='XR_NULL_HANDLE$end$',
                            vscode=VsCodeSnippet('XR_NULL_HANDLE')
                            ))
    snippets.append(Snippet(title='interface',
                            shortcut='interface',
                            description='interface',
                            code='struct $name$ {\n    virtual ~$name$() = default;$end$\n};',
                            literals=[Literal('name', 'name')],
                            vscode=VsCodeSnippet(
                                'struct $1 {\n    virtual ~$1() = default;$0\n};')
                            ))
    snippets.append(Snippet(title='const_ref',
                            shortcut='const_ref',
                            description='const_ref',
                            code='const $name$&$end$',
                            literals=[Literal('name', 'name')],
                            vscode=VsCodeSnippet(
                                'const ${1:name}&')
                            ))

    # Iter
    snippets.append(Snippet(title='begin_end',
                            shortcut='begin_end',
                            description='var.begin(), var.end()',
                            code=r'$var$.begin(), $var$.end()',
                            literals=[Literal('var', 'var')],
                            vscode=VsCodeSnippet(
                                r'${1:name}.begin(), ${1:name}.end()$0')
                            ))

    snippets.append(Snippet(title='TLArg',
                            shortcut='TLArg',
                            description='TLArg(name, "name")',
                            code=r'TLArg($selected$, "$selected$")($end$)',
                            literals=[SelectedTypeLiteral],
                            vscode=VsCodeSnippet(
                                r'TLArg(${1:name}, "${1:name}")$0')
                            ))

    # If find
    snippets.append(Snippet(title='if_map_find',
                            shortcut='if_map_find',
                            description=r'if (auto it = m.find(key); it != m.end()) {}',
                            code='if (auto it = $map$.find($key$); it != $map$.end()){$end$}',
                            literals=[Literal('map', 'map'),
                                      Literal('key', 'key')],
                            vscode=VsCodeSnippet(
                                r'if (auto it = ${1:map}.find(${2:key}); it != ${1:map}.end()){$0}')
                            ))

    # FMT
    snippets.append(Snippet(title='fmt::print',
                            shortcut='fprint',
                            description='fmt::print',
                            code=r'fmt::print("{}", $end$);',
                            vscode=VsCodeSnippet(
                                r'fmt::print("{}", $0);')
                            ))
    snippets.append(Snippet(title='fmt::println',
                            shortcut='fprintln',
                            description='fmt::println',
                            code=r'fmt::print("{}\n", $end$);',
                            vscode=VsCodeSnippet(
                                r'fmt::print("{}\n", $0);')
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
    add_new_snippet_files(snippets)


if __name__ == '__main__':
    main()
