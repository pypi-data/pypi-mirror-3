try:
    # python >= 2.5
    from xml.etree import cElementTree as et
except ImportError:
    import cElementTree as et


from tgwebservices.iconv import _get_single_value, handle_json_params


class Person(object):
    name = str
    age = int
    married = False


def test_complex_conversion_simple_class():
    tree = et.fromstring("""<p>
    <name>Super Value Menu</name>
    <age>17</age>
    <married>no</married>
</p>""")
    val = _get_single_value(tree, Person)
    print val
    assert isinstance(val, Person)
    assert val.age == 17
    assert val.name == "Super Value Menu"
    print val.married
    assert val.married == False


class Family1(object):
    lastname = str
    members = [str]


def test_complex_conversion_with_list():
    tree = et.fromstring("""<family>
    <lastname>Brady</lastname>
    <members>
        <item>Mike</item>
        <item>Carol</item>
        <item>Greg</item>
        <item>Peter</item>
        <item>Bobby</item>
        <item>Marsha</item>
        <item>Jan</item>
        <item>Cindy</item>
    </members>
</family>
""")
    val = _get_single_value(tree, Family1)
    assert val.lastname == "Brady"
    print val.members
    assert len(val.members) == 8
    assert val.members[2] == "Greg"


class Family2(object):
    lastname = str
    members = [Person]


def test_complex_with_list_of_instances():
    tree = et.fromstring("""<family>
    <lastname>Brady</lastname>
    <members>
        <item>
            <name>Mike</name>
            <age>42</age>
        </item>
        <item>
            <name>Carol</name>
            <age>40</age>
        </item>
        <item>
            <name>Greg</name>
            <age>17</age>
        </item>
        <item>
            <name>Peter</name>
            <age>13</age>
        </item>
        <item>
            <name>Bobby</name>
            <age>8</age>
        </item>
        <item>
            <name>Marsha</name>
            <age>16</age>
        </item>
        <item>
            <name>Jan</name>
            <age>13</age>
        </item>
        <item>
            <name>Cindy</name>
            <age>7</age>
        </item>
    </members>
</family>
""")
    val = _get_single_value(tree, Family2)
    assert val.lastname == "Brady"
    print val.members
    assert len(val.members) == 8


def test_list_of_bools():
    tree = et.fromstring("""<list>
    <item>no</item>
    <item>false</item>
    <item>yes</item>
    <item>False</item>
    <item>true</item>
</list>""")
    val = _get_single_value(tree, [bool])
    print val
    assert len(val) == 5


def test_json_conversion_of_class():
    input_types = {"person": Person}
    data = {"person": {"name": "Fred", "age": 99}}
    kw = handle_json_params(data, input_types)
    assert isinstance(kw["person"], Person)
    print kw["person"].age
    assert kw["person"].age == 99
    assert kw["person"].name == "Fred"


def test_json_conversion_of_nested_class():
    input_types = {"family": Family2}
    data = {"family": {"lastname": "Brady", "members":
        [{"name": "Mike", "age": 42}, {"name": "Carol", "age": 40}]}}
    kw = handle_json_params(data, input_types)
    assert isinstance(kw["family"], Family2)
    assert len(kw["family"].members) == 2
    assert kw["family"].members[0].name == "Mike"
    assert kw["family"].members[0].age == 42
