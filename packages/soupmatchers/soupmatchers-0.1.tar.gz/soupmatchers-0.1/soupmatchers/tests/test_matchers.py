"""Tests for the matchers themselves."""

import re

import BeautifulSoup

from testtools import (
    matchers as testtools_matchers,
    TestCase,
    )
from testtools.content import Content
from testtools.content_type import ContentType

import soupmatchers as matchers


anchor_matcher = matchers.Tag("anchor", "a")
image_matcher = matchers.Tag("an image", "image")


class TestResponse(object):

    def __init__(self, status_code=200, content=None):
        self.status_code = status_code
        self.content = content


class StatusCodeMismatchTests(TestCase):

    def test_describe(self):
        mismatch = matchers.StatusCodeMismatch(200, 404)
        self.assertEqual(
            "Got response code 404, expected 200", mismatch.describe())
        mismatch = matchers.StatusCodeMismatch(404, 200)
        self.assertEqual(
            "Got response code 200, expected 404", mismatch.describe())

    def test_get_details_no_html(self):
        mismatch = matchers.StatusCodeMismatch(200, 404)
        self.assertEqual({}, mismatch.get_details())

    def test_get_details_with_html(self):
        html = "<image></image>"
        mismatch = matchers.StatusCodeMismatch(200, 404, html=html)
        self.assertEqual(
            {"html": Content(ContentType("text", "html"), lambda: html)},
            mismatch.get_details())

    def get_equal_mismatches(self):
        html = "<image></image>"
        expected_code = 200
        actual_code = 404
        mismatch1 = matchers.StatusCodeMismatch(
            expected_code, actual_code, html=html)
        mismatch2 = matchers.StatusCodeMismatch(
            expected_code, actual_code, html=html)
        return mismatch1, mismatch2

    def test_eq_equals(self):
        mismatch1, mismatch2 = self.get_equal_mismatches()
        self.assertEqual(mismatch1, mismatch2)

    def test_eq_different_expected(self):
        html = "<image></image>"
        expected_code1 = 200
        expected_code2 = 304
        actual_code = 404
        mismatch1 = matchers.StatusCodeMismatch(
            expected_code1, actual_code, html=html)
        mismatch2 = matchers.StatusCodeMismatch(
            expected_code2, actual_code, html=html)
        self.assertNotEqual(mismatch1, mismatch2)

    def test_eq_different_actual(self):
        html = "<image></image>"
        expected_code = 200
        actual_code1 = 404
        actual_code2 = 304
        mismatch1 = matchers.StatusCodeMismatch(
            expected_code, actual_code1, html=html)
        mismatch2 = matchers.StatusCodeMismatch(
            expected_code, actual_code2, html=html)
        self.assertNotEqual(mismatch1, mismatch2)

    def test_eq_different_html(self):
        html1 = "<image></image>"
        html2 = "<div></div>"
        expected_code = 200
        actual_code = 404
        mismatch1 = matchers.StatusCodeMismatch(
            expected_code, actual_code, html=html1)
        mismatch2 = matchers.StatusCodeMismatch(
            expected_code, actual_code, html=html2)
        self.assertNotEqual(mismatch1, mismatch2)


class ResponseHasTests(TestCase):

    def test_response_has_status_code_matches_200(self):
        response = TestResponse(status_code=200)
        match = matchers.ResponseHas(status_code=200).match(response)
        self.assertEquals(None, match)
        # Check the default value
        match = matchers.ResponseHas().match(response)
        self.assertEquals(None, match)

    def test_response_has_status_code_matches_404(self):
        response = TestResponse(status_code=404)
        match = matchers.ResponseHas(status_code=404).match(response)
        self.assertEquals(None, match)

    def test_response_has_wrong_status_code(self):
        response = TestResponse(status_code=404)
        match = matchers.ResponseHas(status_code=200).match(response)
        self.assertEquals(matchers.StatusCodeMismatch(200, 404), match)

    def test_response_has_wrong_status_code_get_details(self):
        content = "<a></a>"
        response = TestResponse(status_code=404, content=content)
        match = matchers.ResponseHas(status_code=200).match(response)
        self.assertEquals(
            {"html": Content(ContentType("text", "html"), lambda: content)},
            match.get_details())

    def test_response_has_content_matches(self):
        response = TestResponse(content="foo")
        match = matchers.ResponseHas(
            content_matches=testtools_matchers.Equals("foo")).match(response)
        self.assertEquals(None, match)

    def test_response_has_content_mismatch(self):
        response = TestResponse(content="foo")
        match = matchers.ResponseHas(
            content_matches=testtools_matchers.Equals("bar")).match(response)
        # FIXME: a little brittle, define our own mismatcher for this
        # test?
        self.assertEquals(
            testtools_matchers.EqualsMismatch("bar", "foo").describe(),
            match.describe())

    def test_response_has_string_status_code(self):
        response = TestResponse(status_code="404")
        match = matchers.ResponseHas(status_code=404).match(response)
        self.assertEquals(None, match)

    def test_str(self):
        matcher = matchers.ResponseHas(status_code=404)
        self.assertEqual(
            "ResponseHas(status_code=404, content_matches=None)",
            str(matcher))
        html_matcher = matchers.HTMLContains(anchor_matcher)
        matcher = matchers.ResponseHas(
            status_code=200, content_matches=html_matcher)
        self.assertEquals(
            "ResponseHas(status_code=200, content_matches=%s)"
            % str(html_matcher), str(matcher))


class HTMLResponseHasTests(TestCase):

    def test_str(self):
        matcher = matchers.HTMLResponseHas(status_code=404)
        self.assertEqual(
            "HTMLResponseHas(status_code=404, content_matches=None)",
            str(matcher))
        matcher = matchers.HTMLResponseHas(
            status_code=200, html_matches=anchor_matcher)
        html_matcher = matchers.HTMLContains(anchor_matcher)
        self.assertEquals(
            "HTMLResponseHas(status_code=200, content_matches=%s)"
            % str(html_matcher), str(matcher))


class HTMLContainsTests(TestCase):

    def test_zero_matchers(self):
        html_matcher = matchers.HTMLContains()
        self.assertEquals(None, html_matcher.match(""))

    def test_one_matcher_matches(self):
        html_matcher = matchers.HTMLContains(anchor_matcher)
        self.assertEquals(None, html_matcher.match("<a></a>"))

    def test_two_matchers_match(self):
        html_matcher = matchers.HTMLContains(anchor_matcher, image_matcher)
        self.assertEquals(None, html_matcher.match("<a></a><image></image>"))

    def test_one_matcher_mismatches(self):
        html_matcher = matchers.HTMLContains(anchor_matcher)
        content = "<image></image>"
        match = html_matcher.match(content)
        parsed_content = BeautifulSoup.BeautifulSoup(content)
        self.assertEquals(
            matchers.TagMismatch(anchor_matcher, parsed_content, []), match)

    def test_two_matchers_one_mismatches(self):
        html_matcher = matchers.HTMLContains(anchor_matcher, image_matcher)
        content = "<image></image>"
        match = html_matcher.match(content)
        parsed_content = BeautifulSoup.BeautifulSoup(content)
        self.assertEquals(
            matchers.TagMismatch(anchor_matcher, parsed_content, []), match)

    def test_two_matchers_two_mismatch(self):
        html_matcher = matchers.HTMLContains(anchor_matcher, image_matcher)
        content = "<b></b>"
        match = html_matcher.match(content)
        parsed_content = BeautifulSoup.BeautifulSoup(content)
        self.assertEquals(
            matchers.TagMismatch(anchor_matcher, parsed_content, []), match)

    def test_str(self):
        html_matcher = matchers.HTMLContains(anchor_matcher)
        self.assertEquals(
            "HTML contains [%s]" % str(anchor_matcher), str(html_matcher))
        html_matcher = matchers.HTMLContains(anchor_matcher, image_matcher)
        self.assertEquals(
            "HTML contains [%s, %s]" % (
                str(anchor_matcher), str(image_matcher)), str(html_matcher))


class TagMismatchTests(TestCase):

    def test_describe_zero(self):
        content = "<image></image>"
        parsed_content = BeautifulSoup.BeautifulSoup(content)
        mismatch = matchers.TagMismatch(anchor_matcher, parsed_content, [])
        self.assertEqual("Matched 0 times", mismatch.describe())

    def test_describe_one(self):
        content = "<image></image>"
        parsed_content = BeautifulSoup.BeautifulSoup(content)
        mismatch = matchers.TagMismatch(
            anchor_matcher, parsed_content, ["<a></a>"])
        self.assertEqual(
            "Matched 1 time\nThe match was:\n   <a></a>",
            mismatch.describe())

    def test_describe_two(self):
        content = "<image></image>"
        parsed_content = BeautifulSoup.BeautifulSoup(content)
        mismatch = matchers.TagMismatch(
            anchor_matcher, parsed_content, ["<a></a>", "<b></b>"])
        self.assertEqual(
            "Matched 2 times\nThe matches were:\n   <a></a>\n   <b></b>",
            mismatch.describe())

    def test_get_details(self):
        content = "<image></image>"
        parsed_content = BeautifulSoup.BeautifulSoup(content)
        mismatch = matchers.TagMismatch(anchor_matcher, parsed_content, [])
        self.assertEqual(
            {"html": Content(ContentType("text", "html"),
                    lambda: str(parsed_content))}, mismatch.get_details())

    def test_eq_equal(self):
        content = "<image></image>"
        parsed_content = BeautifulSoup.BeautifulSoup(content)
        matches = ["<a></a>"]
        mismatch1 = matchers.TagMismatch(
            anchor_matcher, parsed_content, matches)
        mismatch2 = matchers.TagMismatch(
            anchor_matcher, parsed_content, matches)
        self.assertEqual(mismatch1, mismatch2)

    def test_eq_different_tag(self):
        content = "<image></image>"
        parsed_content = BeautifulSoup.BeautifulSoup(content)
        matches = ["<a></a>"]
        mismatch1 = matchers.TagMismatch(
            anchor_matcher, parsed_content, matches)
        mismatch2 = matchers.TagMismatch(
            image_matcher, parsed_content, matches)
        self.assertNotEqual(mismatch1, mismatch2)

    def test_eq_different_content(self):
        content1 = "<image></image>"
        parsed_content1 = BeautifulSoup.BeautifulSoup(content1)
        content2 = "<div></div>"
        parsed_content2 = BeautifulSoup.BeautifulSoup(content2)
        matches = ["<a></a>"]
        mismatch1 = matchers.TagMismatch(
            anchor_matcher, parsed_content1, matches)
        mismatch2 = matchers.TagMismatch(
            anchor_matcher, parsed_content2, matches)
        self.assertNotEqual(mismatch1, mismatch2)

    def test_eq_different_matches(self):
        content = "<image></image>"
        parsed_content = BeautifulSoup.BeautifulSoup(content)
        matches1 = ["<a></a>"]
        matches2 = ["<b></b>"]
        mismatch1 = matchers.TagMismatch(
            anchor_matcher, parsed_content, matches1)
        mismatch2 = matchers.TagMismatch(
            anchor_matcher, parsed_content, matches2)
        self.assertNotEqual(mismatch1, mismatch2)


class TagTests(TestCase):

    def test_str_count_2(self):
        tag_matcher = matchers.Tag("two anchors", "a", count=2)
        self.assertEqual(
            'Tag("two anchors", <a ...>...</a> (expected 2 times))',
            str(tag_matcher))

    def test_str_count_1(self):
        tag_matcher = matchers.Tag("one anchor", "a", count=1)
        self.assertEqual(
            'Tag("one anchor", <a ...>...</a> (expected 1 time))',
            str(tag_matcher))

    def test_str_attrs(self):
        tag_matcher = matchers.Tag("foo image", "image", attrs={"foo": "bar"})
        self.assertEqual(
            'Tag("foo image", <image foo=\'bar\' ...>...</image>)',
            str(tag_matcher))

    def test_str_multiple_attrs(self):
        tag_matcher = matchers.Tag(
            "foo zap image", "image", attrs={"foo": "bar", "zap": "bang"})
        self.assertEqual(
            'Tag("foo zap image", <image foo=\'bar\' zap=\'bang\' ...>...'
            '</image>)', str(tag_matcher))

    def test_str_text(self):
        tag_matcher = matchers.Tag("bold foo", "b", text="foo")
        self.assertEqual(
            'Tag("bold foo", <b ...>foo ...</b>)',
            str(tag_matcher))

    def test_str_re_text(self):
        tag_matcher = matchers.Tag(
            "bold foo regex", "b", text=re.compile("foo"))
        self.assertEqual(
            'Tag("bold foo regex", <b ...>re.compile(\'foo\') ...</b>)',
            str(tag_matcher))

    def get_match(self, matcher, content):
        parsed_content = BeautifulSoup.BeautifulSoup(content)
        return matcher.match(parsed_content), parsed_content

    def test_matches_one_instance(self):
        content = '<a></a><image></image>'
        tag_matcher = matchers.Tag("one anchor", "a", count=1)
        match, parsed_content = self.get_match(tag_matcher, content)
        self.assertEqual(None, match)

    def test_doesnt_match_two_in_one(self):
        content = '<a></a><image></image>'
        tag_matcher = matchers.Tag("two anchors", "a", count=2)
        match, parsed_content = self.get_match(tag_matcher, content)
        self.assertEquals(
            matchers.TagMismatch(
                tag_matcher, parsed_content, ["<a></a>"]), match)

    def test_matches_two_instances(self):
        content = '<a></a><a></a><image><image/>'
        tag_matcher = matchers.Tag("two anchors", "a", count=2)
        match, parsed_content = self.get_match(tag_matcher, content)
        self.assertEqual(None, match)

    def test_doesnt_match_one_in_two(self):
        content = '<a></a><a></a><image><image/>'
        tag_matcher = matchers.Tag("one anchor", "a", count=1)
        match, parsed_content = self.get_match(tag_matcher, content)
        self.assertEquals(
            matchers.TagMismatch(
                tag_matcher, parsed_content, ["<a></a>", "<a></a>"]), match)

    def test_matches_any_number_one(self):
        content = '<a></a><image><image/>'
        match, parsed_content = self.get_match(anchor_matcher, content)
        self.assertEquals(None, match)

    def test_matches_any_number_more(self):
        content = '<a></a><a></a><image><image/>'
        match, parsed_content = self.get_match(anchor_matcher, content)
        self.assertEquals(None, match)

    def test_matches_attributes(self):
        content = '<a href="/foo"></a>'
        tag_matcher = matchers.Tag("foo anchor", "a", attrs={"href": "/foo"})
        match, parsed_content = self.get_match(tag_matcher, content)
        self.assertEqual(None, match)

    def test_doesnt_match_missing_attributes(self):
        content = '<a href="/foo"></a>'
        tag_matcher = matchers.Tag(
            "class foo anchor", "a", attrs={"class": "/foo"})
        match, parsed_content = self.get_match(tag_matcher, content)
        self.assertEquals(
            matchers.TagMismatch(tag_matcher, parsed_content, []), match)

    def test_matches_multiple_attributes(self):
        content = '<a href="/foo" class="foo"></a>'
        tag_matcher = matchers.Tag(
            "class foo href foo anchor", "a",
            attrs={"class": "foo", "href": "/foo"})
        match, parsed_content = self.get_match(tag_matcher, content)
        self.assertEqual(None, match)

    def test_matches_text(self):
        content = '<a>Some text</a>'
        tag_matcher = matchers.Tag(
            "a with text", "a", text="Some text")
        match, parsed_content = self.get_match(tag_matcher, content)
        self.assertEqual(None, match)

    def test_doesnt_match_other_text(self):
        content = '<a>Some other text</a>'
        tag_matcher = matchers.Tag("a with text", "a", text="Some text")
        match, parsed_content = self.get_match(tag_matcher, content)
        self.assertEqual(
            matchers.TagMismatch(tag_matcher, parsed_content, []), match)

    def test_doesnt_match_missing_text(self):
        content = '<a></a>'
        tag_matcher = matchers.Tag("a with text", "a", text="Some text")
        match, parsed_content = self.get_match(tag_matcher, content)
        self.assertEqual(
            matchers.TagMismatch(tag_matcher, parsed_content, []), match)

    def test_matches_tag_name_regex(self):
        content = '<body><a><b></b></a></body>'
        tag_matcher = matchers.Tag("two b* tags", re.compile(r"^b"), count=2)
        match, parsed_content = self.get_match(tag_matcher, content)
        self.assertEqual(None, match)

    def test_matches_tag_name_list(self):
        content = '<a></a><b></b>'
        tag_matcher = matchers.Tag(
            "two a b or image tags", ["a", "b", "image"], count=2)
        match, parsed_content = self.get_match(tag_matcher, content)
        self.assertEqual(None, match)

    def test_matches_tag_name_dict(self):
        content = '<a></a><b></b>'
        tag_matcher = matchers.Tag(
            "two a b or image tags", dict(a=True, b=True, image=True),
            count=2)
        match, parsed_content = self.get_match(tag_matcher, content)
        self.assertEqual(None, match)

    def test_matches_all_tags_on_true(self):
        content = '<a></a><b></b>'
        tag_matcher = matchers.Tag("two tags of any type", True, count=2)
        match, parsed_content = self.get_match(tag_matcher, content)
        self.assertEqual(None, match)

    def test_matches_match_func(self):
        content = '<a class="foo"></a><b></b>'
        tag_matcher = matchers.Tag(
            "tag without attrs", lambda tag: len(tag.attrs) == 0)
        match, parsed_content = self.get_match(tag_matcher, content)
        self.assertEqual(None, match)

    def test_matches_attrs_regex(self):
        content = ('<p id="firstpara"></p><p id="secondpara">'
                '</p><p id="other"></p>')
        tag_matcher = matchers.Tag(
            "2 p tags with ids ending with para", 'p',
            attrs=dict(id=re.compile(r'para$')), count=2)
        match, parsed_content = self.get_match(tag_matcher, content)
        self.assertEqual(None, match)

    def test_matches_attrs_list(self):
        content = '<p id="first"></p><p id="second"></p><p id="other"></p>'
        tag_matcher = matchers.Tag(
            "two p tags with ids of first second or none", 'p',
            attrs=dict(id=["first", "second", "none"]), count=2)
        match, parsed_content = self.get_match(tag_matcher, content)
        self.assertEqual(None, match)

    def test_matches_attrs_dict(self):
        content = '<p id="first"></p><p id="second"></p><p id="other"></p>'
        tag_matcher = matchers.Tag(
            "two p tags with ids of first second or none", 'p',
            attrs=dict(id=dict(first=True, second=True, none=True)),
                count=2)
        match, parsed_content = self.get_match(tag_matcher, content)
        self.assertEqual(None, match)

    def test_matches_attrs_true(self):
        content = '<p id="first"></p><p id="second"></p><p></p>'
        tag_matcher = matchers.Tag(
            "two p tags with ids", 'p', attrs=dict(id=True), count=2)
        match, parsed_content = self.get_match(tag_matcher, content)
        self.assertEqual(None, match)

    def test_matches_attrs_none(self):
        content = '<p id="first"></p><p id="second"></p><p></p>'
        tag_matcher = matchers.Tag(
            "one p tags without an id", 'p', attrs=dict(id=None), count=1)
        match, parsed_content = self.get_match(tag_matcher, content)
        self.assertEqual(None, match)

    def test_matches_attrs_callable(self):
        content = '<p id="first"></p><p id="second"></p><p></p>'
        tag_matcher = matchers.Tag(
            "two p tags with ids", 'p',
            attrs=dict(id=lambda attrs: attrs != None), count=2)
        match, parsed_content = self.get_match(tag_matcher, content)
        self.assertEqual(None, match)

    def test_matches_text_and_tag(self):
        content = '<a>foo</a><b>foo</b>'
        tag_matcher = matchers.Tag("foo link", 'a', text="foo")
        match, parsed_content = self.get_match(tag_matcher, content)
        self.assertEqual(None, match)

    def test_get_extra_info_no_close_matches(self):
        content = "<image></image>"
        parsed_content = BeautifulSoup.BeautifulSoup(content)
        extra_info = anchor_matcher.get_extra_info([parsed_content], "")
        self.assertEqual([], extra_info)

    def test_get_extra_info_vary_attributes(self):
        tag_matcher = matchers.Tag("foo link", "a", attrs={"href": "foo"})
        content = "<a></a>"
        parsed_content = BeautifulSoup.BeautifulSoup(content)
        close_matches = tag_matcher.get_extra_info([parsed_content], "")
        self.assertEqual(
            ['1 matches for "foo link" when attribute href="foo" '
             'is not a requirement.'], close_matches)

    def test_get_extra_info_vary_two_attributes(self):
        tag_matcher = matchers.Tag(
            "foo bar link", "a", attrs={"href": "foo", "class": "bar"})
        content = "<a href='foo'></a><a class='bar'></a>"
        parsed_content = BeautifulSoup.BeautifulSoup(content)
        extra_info = tag_matcher.get_extra_info([parsed_content], "")
        self.assertEqual(
            ['1 matches for "foo bar link" when attribute class="bar" '
             'is not a requirement.',
             '1 matches for "foo bar link" when attribute href="foo" '
             'is not a requirement.'],
            sorted(extra_info))

    def test_get_extra_info_vary_text(self):
        tag_matcher = matchers.Tag("bold rocks", "b", text="rocks")
        content = "<b>is awesome</b>"
        parsed_content = BeautifulSoup.BeautifulSoup(content)
        extra_info = tag_matcher.get_extra_info([parsed_content], "")
        self.assertEqual(
            ['1 matches for \"bold rocks\" when text="rocks" is not a '
            'requirement.'], extra_info)

    def test_get_extra_info_more_matches_than_wanted(self):
        tag_matcher = matchers.Tag(
            "no bold rocks", "b", text="rocks", count=0)
        content = "<b>is awesome</b>"
        parsed_content = BeautifulSoup.BeautifulSoup(content)
        extra_info = tag_matcher.get_extra_info([parsed_content], "")
        self.assertEqual([], extra_info)

    def test_get_extra_info_multiple_roots(self):
        tag_matcher = matchers.Tag("bold rocks", "b", text="rocks")
        content1 = "<b>is awesome</b>"
        parsed_content1 = BeautifulSoup.BeautifulSoup(content1)
        content2 = "<b>is awesome</b>"
        parsed_content2 = BeautifulSoup.BeautifulSoup(content2)
        extra_info = tag_matcher.get_extra_info(
            [parsed_content1, parsed_content2], "")
        self.assertEqual(
            ['2 matches for \"bold rocks\" when text="rocks" is not a '
            'requirement.'], extra_info)

    def test_get_extra_info_identifier_suffix(self):
        tag_matcher = matchers.Tag("bold rocks", "b", text="rocks")
        content = "<b>is awesome</b>"
        parsed_content = BeautifulSoup.BeautifulSoup(content)
        extra_info = tag_matcher.get_extra_info([parsed_content],
                " within foo")
        self.assertEqual(
            ['1 matches for \"bold rocks\" within foo when text="rocks" '
            'is not a requirement.'], extra_info)


class TagWithIdTests(TestCase):

    def test_returns_Tag_instance(self):
        tag_matcher = matchers.TagWithId('foo')
        self.assertIsInstance(tag_matcher, matchers.Tag)

    def test_sets_identifier_based_on_id(self):
        tag_matcher = matchers.TagWithId('foo')
        self.assertEqual('#foo', tag_matcher._identifier)

    def test_sets_tag_type_to_True(self):
        tag_matcher = matchers.TagWithId('foo')
        self.assertEqual(True, tag_matcher.tag_type)

    def test_sets_attrs_to_id(self):
        tag_matcher = matchers.TagWithId('foo')
        self.assertEqual({'id': 'foo'}, tag_matcher.attrs)

    def test_allows_overriding_identifier(self):
        tag_matcher = matchers.TagWithId('foo', 'some identifier')
        self.assertEqual('some identifier', tag_matcher._identifier)

    def test_allows_setting_tag_type(self):
        tag_matcher = matchers.TagWithId('foo', tag_type='a')
        self.assertEqual('a', tag_matcher.tag_type)

    def test_allows_setting_attrs(self):
        tag_matcher = matchers.TagWithId('foo', attrs={'bar': 'baz'})
        self.assertEqual({'id': 'foo', 'bar': 'baz'}, tag_matcher.attrs)

    def test_overrides_id_in_attrs(self):
        tag_matcher = matchers.TagWithId('foo', attrs={'id': 'baz'})
        self.assertEqual({'id': 'foo'}, tag_matcher.attrs)

    def test_allows_setting_text(self):
        tag_matcher = matchers.TagWithId('foo', text="bar")
        self.assertEqual('bar', tag_matcher.text)

    def test_allows_setting_count(self):
        tag_matcher = matchers.TagWithId('foo', count=2)
        self.assertEqual(2, tag_matcher.count)


class WithinTests(TestCase):

    def test_str(self):
        within_matcher = matchers.Within(anchor_matcher, image_matcher)
        self.assertEqual(
            "%s within %s" % (image_matcher, anchor_matcher),
            str(within_matcher))

    def test_match_outer_not_matched(self):
        within_matcher = matchers.Within(anchor_matcher, image_matcher)
        content = "<image></image>"
        parsed_content = BeautifulSoup.BeautifulSoup(content)
        mismatch = within_matcher.match(parsed_content)
        self.assertEqual(
            matchers.TagMismatch(within_matcher, parsed_content, []),
            mismatch)

    def test_match_mismatch(self):
        within_matcher = matchers.Within(anchor_matcher, image_matcher)
        content = "<a></a><image></image>"
        parsed_content = BeautifulSoup.BeautifulSoup(content)
        mismatch = within_matcher.match(parsed_content)
        self.assertEqual(
            matchers.TagMismatch(within_matcher, parsed_content, []),
            mismatch)

    def test_match_match_in_one(self):
        within_matcher = matchers.Within(anchor_matcher, image_matcher)
        content = "<a><image></image></a>"
        parsed_content = BeautifulSoup.BeautifulSoup(content)
        mismatch = within_matcher.match(parsed_content)
        self.assertEqual(None, mismatch)

    def test_match_tag_within_itself(self):
        """Check that the descendents aren't evaluated against matched tag.

        If we aren't careful then we can have a descendents clause matched
        by the tag itself. This won't usually catch people out, but when
        it does we should make sure we do the right thing.
        """
        content = '<div><div></div></div>'
        child_matcher = matchers.Tag("div", 'div')
        tag_matcher = matchers.Within(child_matcher, child_matcher)
        parsed_content = BeautifulSoup.BeautifulSoup(content)
        match = tag_matcher.match(parsed_content)
        self.assertEqual(None, match)

    def test_mismatch_tag_within_itself(self):
        """Check that the descendents aren't evaluated against matched tag.

        If we aren't careful then we can have a descendents clause matched
        by the tag itself. This won't usually catch people out, but when
        it does we should make sure we do the right thing.
        """
        content = '<div><span></span></div>'
        child_matcher = matchers.Tag("div", 'div')
        tag_matcher = matchers.Within(child_matcher, child_matcher)
        parsed_content = BeautifulSoup.BeautifulSoup(content)
        match = tag_matcher.match(parsed_content)
        self.assertEqual(
            matchers.TagMismatch(tag_matcher, parsed_content, []),
            match)

    def test_get_extra_info_both_missing(self):
        content = ''
        tag_matcher = matchers.Within(anchor_matcher, image_matcher)
        parsed_content = BeautifulSoup.BeautifulSoup(content)
        extra_info = tag_matcher.get_extra_info([parsed_content], "")
        self.assertEqual(
            ['0 matches for "%s" in the document.'
                % image_matcher.identifier,
             '0 matches for "%s" in the document.'
                % anchor_matcher.identifier],
            extra_info)

    def test_get_extra_info_inner_missing(self):
        content = '<a></a>'
        tag_matcher = matchers.Within(anchor_matcher, image_matcher)
        parsed_content = BeautifulSoup.BeautifulSoup(content)
        extra_info = tag_matcher.get_extra_info([parsed_content], "")
        self.assertEqual(
            ['0 matches for "%s" in the document.'
                % image_matcher.identifier,
             '1 matches for "%s" in the document.'
                % anchor_matcher.identifier],
            extra_info)

    def test_get_extra_info_neither_missing(self):
        content = '<a></a><image></image>'
        tag_matcher = matchers.Within(anchor_matcher, image_matcher)
        parsed_content = BeautifulSoup.BeautifulSoup(content)
        extra_info = tag_matcher.get_extra_info([parsed_content], "")
        self.assertEqual(
            ['1 matches for "%s" in the document.'
                % image_matcher.identifier,
             '1 matches for "%s" in the document.'
                % anchor_matcher.identifier],
            extra_info)

    def test_get_extra_close_matches(self):
        content = '<a><b>is awesome</b></a>'
        bold_matcher = matchers.Tag("bold rocks", "b", text="rocks")
        tag_matcher = matchers.Within(anchor_matcher, bold_matcher)
        parsed_content = BeautifulSoup.BeautifulSoup(content)
        extra_info = tag_matcher.get_extra_info([parsed_content], "")
        self.assertEqual(
            ['0 matches for "bold rocks" in the document.',
             '1 matches for "%s" in the document.'
                % anchor_matcher.identifier,
             '1 matches for "bold rocks" within "%s" when text="rocks" is '
             'not a requirement.' % anchor_matcher.identifier],
            extra_info)

    def test_get_extra_info_multiple_parts(self):
        content = '<a></a><image></image>'
        tag_matcher = matchers.Within(anchor_matcher, image_matcher)
        parsed_content = BeautifulSoup.BeautifulSoup(content)
        extra_info = tag_matcher.get_extra_info(
            [parsed_content, parsed_content], "")
        self.assertEqual(
            ['2 matches for "%s" in the document.'
                % image_matcher.identifier,
             '2 matches for "%s" in the document.'
                % anchor_matcher.identifier],
            extra_info)

    def test_get_extra_info_with_suffix(self):
        content = '<a></a><image></image>'
        tag_matcher = matchers.Within(anchor_matcher, image_matcher)
        parsed_content = BeautifulSoup.BeautifulSoup(content)
        extra_info = tag_matcher.get_extra_info([parsed_content],
                " within foo")
        self.assertEqual(
            ['1 matches for "%s" within foo in the document.'
                % image_matcher.identifier,
             '1 matches for "%s" within foo in the document.'
                % anchor_matcher.identifier],
            extra_info)

    def test_get_matches(self):
        within_matcher = matchers.Within(anchor_matcher, image_matcher)
        content = "<a><image></image></a>"
        parsed_content = BeautifulSoup.BeautifulSoup(content)
        matches = within_matcher.get_matches(parsed_content)
        self.assertEqual([content], [str(a) for a in matches])

    def test_identifier(self):
        within_matcher = matchers.Within(anchor_matcher, image_matcher)
        self.assertEqual('"%s" within "%s"' % (image_matcher.identifier,
                    anchor_matcher.identifier), within_matcher.identifier)


class DocumentPartTests(TestCase):

    def test_within_rejects_non_tag(self):
        within_matcher = matchers.Within(anchor_matcher, image_matcher)
        self.assertRaises(ValueError, anchor_matcher.within, within_matcher)

    def test_within_returns_a_within(self):
        within_matcher = image_matcher.within(anchor_matcher)
        self.assertIsInstance(within_matcher, matchers.Within)

    def test_within_has_correct_outer(self):
        within_matcher = image_matcher.within(anchor_matcher)
        self.assertEqual(anchor_matcher, within_matcher.outer)

    def test_within_has_correct_inner(self):
        within_matcher = image_matcher.within(anchor_matcher)
        self.assertEqual(image_matcher, within_matcher.inner)

    def test_within_works_on_a_within(self):
        inner_within = matchers.Within(anchor_matcher, image_matcher)
        within_matcher = inner_within.within(anchor_matcher)
        self.assertEqual(inner_within, within_matcher.inner)


class FormTests(TestCase):

    def test_tag_type(self):
        form_matcher = matchers.Form("a form")
        self.assertEqual("form", form_matcher.tag_type)

    def test_set_method(self):
        form_matcher = matchers.Form("a form", method="POST")
        self.assertEqual("POST", form_matcher.attrs["method"])

    def test_set_action(self):
        form_matcher = matchers.Form("a form", action="action.asp")
        self.assertEqual("action.asp", form_matcher.attrs["action"])


class SelectTests(TestCase):

    def test_identifier(self):
        select_matcher = matchers.Select("some select")
        self.assertEqual("some select", select_matcher.identifier)

    def test_select_matcher_identifier(self):
        select_matcher = matchers.Select("some select")
        self.assertEqual("some select <select> tag",
            select_matcher.select_matcher.identifier)

    def test_select_matcher_tag_type(self):
        select_matcher = matchers.Select("some select")
        self.assertEqual("select",
            select_matcher.select_matcher.tag_type)

    def test_select_matcher_name_attribute(self):
        select_matcher = matchers.Select("some select", name="options")
        self.assertEqual({"name": "options"},
            select_matcher.select_matcher.attrs)

    def test_select_matcher_passes_attrs(self):
        select_matcher = matchers.Select("some select", name="options",
                attrs={"name": "some_other", "class": "some_class"})
        self.assertEqual({"name": "options", "class": "some_class"},
            select_matcher.select_matcher.attrs)

    def get_select_matcher_with_single_choice(self):
        return matchers.Select("some select", choices={"choice1": "Choice 1"})

    def test_choice_matchers_is_MatchesAll(self):
        select_matcher = self.get_select_matcher_with_single_choice()
        self.assertIsInstance(select_matcher.choice_matchers,
                testtools_matchers.MatchesAll)

    def test_single_choice_gives_single_choice_matcher(self):
        select_matcher = self.get_select_matcher_with_single_choice()
        self.assertEqual(1, len(select_matcher.choice_matchers.matchers))

    def test_choice_matcher_is_tag(self):
        select_matcher = self.get_select_matcher_with_single_choice()
        self.assertIsInstance(
                select_matcher.choice_matchers.matchers[0],
                matchers.Tag)

    def test_choice_matcher_identifier(self):
        select_matcher = self.get_select_matcher_with_single_choice()
        self.assertEqual("some select choice1 option",
                select_matcher.choice_matchers.matchers[0].identifier)

    def test_choice_matcher_tag_type(self):
        select_matcher = self.get_select_matcher_with_single_choice()
        self.assertEqual("option",
                select_matcher.choice_matchers.matchers[0].tag_type)

    def test_choice_matcher_attrs(self):
        select_matcher = self.get_select_matcher_with_single_choice()
        self.assertEqual({"value": "choice1"},
                select_matcher.choice_matchers.matchers[0].attrs)

    def test_choice_matcher_text(self):
        select_matcher = self.get_select_matcher_with_single_choice()
        self.assertEqual("Choice 1",
                select_matcher.choice_matchers.matchers[0].text)

    def test_choice_matcher_with_two_choices_gives_two_matchers(self):
        select_matcher = matchers.Select("some select",
            choices={"choice1": "Choice 1", "choice2": "Choice 2"})
        self.assertEqual(2, len(select_matcher.choice_matchers.matchers))

    def test_choice_matcher_with_no_choices_gives_no_matchers(self):
        select_matcher = matchers.Select("some select")
        self.assertEqual(0, len(select_matcher.choice_matchers.matchers))

    def test_str(self):
        select_matcher = matchers.Select("some select", name="foo",
            choices={"choice1": "Choice 1", "choice2": "Choice 2"})
        self.assertEqual("[%s] within %s"
            % (", ".join([str(a) for a
                    in select_matcher.choice_matchers.matchers]),
                select_matcher.select_matcher),
            str(select_matcher))

    def test_get_matches_outer_missing(self):
        select_matcher = self.get_select_matcher_with_single_choice()
        content = '<option value="choice1">Choice 1</option>'
        parsed_content = BeautifulSoup.BeautifulSoup(content)
        matches = select_matcher.get_matches(parsed_content)
        self.assertEqual([], matches)

    def test_get_matches_one_inner_missing(self):
        select_matcher = matchers.Select("some select", name="foo",
            choices={"choice1": "Choice 1", "choice2": "Choice 2"})
        content = ('<select name="foo"><option value="choice1">'
                'Choice 1</option></select>')
        parsed_content = BeautifulSoup.BeautifulSoup(content)
        matches = select_matcher.get_matches(parsed_content)
        self.assertEqual([], matches)

    def test_get_matches_matches(self):
        select_matcher = matchers.Select("some select", name="foo",
            choices={"choice1": "Choice 1", "choice2": "Choice 2"})
        content = ('<select name="foo"><option value="choice1">'
                'Choice 1</option><option value="choice2">'
                'Choice 2</option></select>')
        parsed_content = BeautifulSoup.BeautifulSoup(content)
        matches = select_matcher.get_matches(parsed_content)
        self.assertEqual([content], [str(a) for a in matches])

    def test_single_match(self):
        select_matcher = matchers.Select("some select", name="foo",
            choices={"choice1": "Choice 1", "choice2": "Choice 2"})
        content = ('<select name="foo"><option value="choice1">'
                'Choice 1</option><option value="choice2">'
                'Choice 2</option></select>')
        unmatched_content = ('<select name="foo"><option value="choice1">'
                'Choice 1</option></select>')
        parsed_content = BeautifulSoup.BeautifulSoup(
                content+unmatched_content)
        matches = select_matcher.get_matches(parsed_content)
        self.assertEqual([content], [str(a) for a in matches])

    def test_match_twice(self):
        select_matcher = self.get_select_matcher_with_single_choice()
        content = '<select><option value="choice1">Choice 1</option></select>'
        parsed_content = BeautifulSoup.BeautifulSoup(content*2)
        matches = select_matcher.get_matches(parsed_content)
        self.assertEqual([content]*2, [str(a) for a in matches])


def load_tests(loader, standard_tests, pattern):
    import doctest
    import os
    import sys
    import unittest
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    suite.addTest(loader.loadTestsFromName(__name__))
    source_readme_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "README")
    if os.path.exists(source_readme_path):
        suite.addTest(
            doctest.DocFileTest(os.path.relpath(
                    source_readme_path, os.path.dirname(__file__)),
                optionflags=doctest.NORMALIZE_WHITESPACE))
    else:
        sys.stderr.write("Warning: not testing README as it can't be found")
    return suite
