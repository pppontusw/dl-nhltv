from nhltv_lib.arguments import parse_args


def test_parse_args(arguments_list):
    argies = parse_args(arguments_list)
    assert argies.username == "username"
    assert argies.password == "password"
    assert argies.quality == "3333"
