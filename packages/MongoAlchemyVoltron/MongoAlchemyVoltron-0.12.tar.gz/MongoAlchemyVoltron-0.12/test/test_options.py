"""
Tests for mongoalchemy.options

"""
from nose.tools import *

from mongoalchemy import options
from mongoalchemy.document import Document
from mongoalchemy.fields import Field


DEFAULTS = None

def setup():
    # Let's always start with the same defaults, yea?
    global DEFAULTS
    if not DEFAULTS:
        DEFAULTS = options.CONFIG.copy()
    else:
        options.CONFIG = DEFAULTS.copy()


def _req():
    # We're testing against this a lot
    return options.CONFIG['required']


def test_options_update():
    options.configure(namespace='foobar')
    assert options.CONFIG['namespace'] == 'foobar'


def test_document_options_transparency():
    class D(Document):
        pass
    # Change an option
    options.configure(required=not _req())
    # And make sure it shows up
    assert D.config_required == _req()
    assert D().config_required == _req()


def test_field_options_transparency():
    class F(Field):
        pass
    # Change an option
    options.configure(required=not _req())
    # And make sure it shows up
    assert F.required == _req()
    assert F().required == _req()


def test_document_options_opacity():
    class D(Document):
        config_required = not _req()
    # Make sure it's different
    assert D.config_required != _req()
    assert D().config_required != _req()


def test_field_options_opacity1():
    class F(Field):
        required = not _req()
    # Make sure it's different
    assert F.required != _req()
    assert F().required != _req()


def test_field_options_opacity2():
    class F(Field):
        pass
    # Make sure it's different
    assert F(required=not _req()).required != _req()


def test_field_inherited_opacity():
    class D(Document):
        config_required = not _req()
        f = Field()
    # Make sure it's different
    assert D.f.required != _req()
    assert D()._fields['f'].required != _req()


def test_global_inheriting():
    class D(Document):
        f = Field()
    options.configure(required=not _req())
    # Make sure it goes all the way down
    assert D.f.required == _req()
    assert D()._fields['f'].required == _req()


def test_cls_modification():
    class D(Document):
        f = Field()
    D.config_required = not _req()
    # Make sure it goes all the way down
    assert D.f.required != _req()
    assert D()._fields['f'].required != _req()


def test_configure_with_dict():
    options.configure({'namespace':'foobar'})
    assert options.CONFIG['namespace'] == 'foobar'


@raises(TypeError)
def test_too_many_args():
    options.configure({}, {})


@raises(TypeError)
def test_wrong_arg():
    options.configure(1)


@raises(ValueError)
def test_stupid_option():
    options.configure(foobar=True)

