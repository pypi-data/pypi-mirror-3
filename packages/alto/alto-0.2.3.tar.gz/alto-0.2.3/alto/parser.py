import ast
import importlib
import inspect
import pprint

# TODO: Find full paths to callbacks
# TODO: Parse class instantiation for callbacks
# TODO: Handle pattern expressions instead of just strings
# TODO: Split into mutiple functions

def parse_pattern_regex(node):
    if isinstance(node, ast.Str):
        return node.s
    print ast.dump(node)
    print compile(node, '<string>', 'eval')
    # return ast.literal_eval(node)
    raise Exception('CRAP')

def parse_patterns(root_urlconf, url_prefix=''):
    """
    Import and parse urlpatterns from the given path.
    """
    module = importlib.import_module(root_urlconf)
    filename = inspect.getsourcefile(module)
    with open(filename) as fh:
        source = fh.read()

    context = {}
    tree = ast.parse(source)
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Assign) and node.targets[0].id != 'urlpatterns':
            context[node.targets[0].id] = node.value
        if isinstance(node, ast.Assign) and node.targets[0].id == 'urlpatterns':
            prefix = node.value.args[0].s
            for arg in node.value.args[1:]:
                if isinstance(arg, ast.Call):
                    components = arg.args
                elif isinstance(arg, ast.Tuple):
                    components = arg.elts
                else:
                    raise Exception('Invalid argument to urlpatterns was found.')

                if len(components) == 2:
                    regex_node, callback_node = components
                    default_args_node = None
                elif len(components) == 3:
                    regex_node, callback_node, default_args_node = components

                if isinstance(callback_node, ast.Attribute):
                    callback = '.'.join((callback_node.value.id, callback_node.attr))
                    pprint.pprint({
                        'url_prefix': url_prefix,
                        'prefix': prefix,
                        'line': arg.lineno,
                        'filename': filename,
                        'regex': parse_pattern_regex(regex_node),
                        'callback': callback,
                    })
                elif isinstance(callback_node, ast.Call):
                    if isinstance(callback_node.func, ast.Name) and callback_node.func.id == 'include':
                        url_prefix = parse_pattern_regex(regex_node)
                        included_urlconf_path = callback_node.args[0].s
                        parse_patterns(included_urlconf_path, url_prefix)
                        # print ast.dump(callback_node)
                        # print ast.dump(callback_node)
        print context

if __name__ == '__main__':
    parse_patterns('alto.tests.urls')
    # parse_patterns('everyblock.web.urls')
