# -*- coding: utf-8 -*-

"""
Qt4 TS file parser for Python
"""
import re
import time
import xml.dom.minidom
import xml.parsers.expat
from xml.sax.saxutils import escape as xml_escape
from django.db import transaction
from django.db.models import get_model
from django.utils.translation import ugettext, ugettext_lazy as _
from transifex.txcommon.log import logger
from transifex.txcommon.exceptions import FileCheckError
from transifex.resources.formats.core import ParseError, CompileError, \
        Handler, STRICT
from transifex.resources.formats.resource_collections import StringSet, \
        GenericTranslation
from suggestions.models import Suggestion
from transifex.resources.formats.utils.decorators import *
from transifex.resources.formats.utils.hash_tag import hash_tag, escape_context


# Resources models
Resource = get_model('resources', 'Resource')
Translation = get_model('resources', 'Translation')
SourceEntity = get_model('resources', 'SourceEntity')


class LinguistParseError(ParseError):
    pass


class LinguistCompileError(CompileError):
    pass


def _getElementByTagName(element, tagName, noneAllowed = False):
    elements = element.getElementsByTagName(tagName)
    if not noneAllowed and not elements:
        raise LinguistParseError("Element '%s' not found!" % tagName)
    if len(elements) > 1:
        raise LinguistParseError("Multiple '%s' elements found!" % tagName)
    return elements[0]

def _get_attribute(element, key, die = False):
    if element.attributes.has_key(key):
        return element.attributes[key].value
    elif die:
        raise LinguistParseError("Could not find attribute '%s' "\
            "for element '%s'" % (key, element.tagName))
    else:
        return None

def _getText(nodelist):
    rc = []
    for node in nodelist:
        if hasattr(node, 'data'):
            rc.append(node.data)
        else:
            rc.append(node.toxml())
    return ''.join(rc)


class LinguistHandler(Handler):
    name = "Qt4 TS parser"
    format = "Qt4 Translation XML files (*.ts)"
    method_name = 'QT'

    HandlerParseError = LinguistParseError
    HandlerCompileError = LinguistCompileError

    def _escape(self, s):
        return xml_escape(s, {"'": "&apos;", '"': '&quot;'})

    def _post_compile(self, *args, **kwargs):
        """
        """
        if hasattr(kwargs,'language'):
            language = kwargs['language']
        else:
            language = self.language

        doc = xml.dom.minidom.parseString(self.compiled_template)
        root = doc.documentElement
        root.attributes["language"] = language.code

        for message in doc.getElementsByTagName("message"):
            translation = _getElementByTagName(message, "translation")
            if message.attributes.has_key("numerus") and \
                message.attributes['numerus'].value=='yes':
                source = _getElementByTagName(message, "source")
                numerusforms = message.getElementsByTagName('numerusform')
                translation.childNodes  = []

                # If we have an id for the message use this as the source
                # string, otherwise use the actual source string
                if message.attributes.has_key("id"):
                    sourceString = message.attributes['id'].value
                else:
                    sourceString = _getText(source.childNodes)

                plurals = Translation.objects.filter(
                    resource=self.resource,
                    language=language,
                    source_entity__string=sourceString,
                    source_entity__context=self._context_of_message(message)
                ).order_by('rule')

                plural_keys = {}
                # last rule excluding other(5)
                lang_rules = language.get_pluralrules_numbers()
                # Initialize all plural rules up to the last
                for p,n in enumerate(lang_rules):
                    plural_keys[p] = ""
                for p,n in enumerate(plurals):
                    plural_keys[p] = n.string
                message.setAttribute('numerus', 'yes')
                for key in plural_keys.iterkeys():
                    e = doc.createElement("numerusform")
                    e.appendChild(
                        doc.createTextNode(
                            self._pseudo_decorate(plural_keys[key])
                        )
                    )
                    translation.appendChild(e)
                    if not plural_keys[key]:
                        translation.attributes['type'] = 'unfinished'
            else:
                if not translation.childNodes:
                    translation.attributes['type'] = 'unfinished'

        template_text = doc.toxml()
        esc_template_text = re.sub("'(?=(?:(?!>).)*<\/source>)",
            r"&apos;", template_text)
        esc_template_text = re.sub("'(?=(?:(?!>).)*<\/translation>)",
            r"&apos;", esc_template_text)
        self.compiled_template = esc_template_text

    def _context_of_message(self, message):
        """Get the context value of a message node."""
        context_node = message.parentNode
        context_name_element = _getElementByTagName(context_node, "name")
        if context_name_element.firstChild:
            if context_name_element.firstChild.nodeValue:
                context_name = escape_context(
                    [context_name_element.firstChild.nodeValue])
            else:
                context_name = []
        else:
            context_name = []
        try:
            c_node = _getElementByTagName(message, "comment")
            comment_text = _getText(c_node.childNodes)
            if comment_text:
                comment = escape_context([comment_text])
            else:
                comment = []
        except LinguistParseError, e:
            comment = []
        return (context_name + comment) or "None"

    def _parse(self, is_source, lang_rules):
        """
        Parses Qt file and exports all entries as GenericTranslations.
        """
        def clj(s, w):
            return s[:w].replace("\n", " ").ljust(w)

        if lang_rules:
            nplural = len(lang_rules)
        else:
            nplural = self.language.get_pluralrules_numbers()

        try:
            doc = xml.dom.minidom.parseString(
                self.content.encode(self.format_encoding)
            )
        except Exception, e:
            logger.warning("QT parsing: %s" % e.message, exc_info=True)
            raise LinguistParseError(
                "Your file doesn't seem to contain valid xml: %s!" % e.message
            )
        if hasattr(doc, 'doctype') and hasattr(doc.doctype, 'name'):
            if doc.doctype.name != "TS":
                raise LinguistParseError("Incorrect doctype!")
        else:
            raise LinguistParseError("Uploaded file has no Doctype!")
        root = doc.documentElement
        if root.tagName != "TS":
            raise LinguistParseError("Root element is not 'TS'")

        # This needed to be commented out due the 'is_source' parameter.
        # When is_source=True we return the value of the <source> node as the
        # translation for the given file, instead of the <translation> node(s).
        #stringset.target_language = language
        #language = get_attribute(root, "language", die = STRICT)

        i = 1
        # There can be many <message> elements, they might have
        # 'encoding' or 'numerus' = 'yes' | 'no' attributes
        # if 'numerus' = 'yes' then 'translation' element contains 'numerusform' elements
        for context in root.getElementsByTagName("context"):
            context_name_element = _getElementByTagName(context, "name")
            if context_name_element.firstChild:
                if context_name_element.firstChild.nodeValue:
                    context_name = escape_context(
                        [context_name_element.firstChild.nodeValue])
                else:
                    context_name = []
            else:
                context_name = []

            for message in context.getElementsByTagName("message"):
                occurrences = []

                # NB! There can be zero to many <location> elements, but all
                # of them must have 'filename' and 'line' attributes
                for location in message.getElementsByTagName("location"):
                    if location.attributes.has_key("filename") and \
                        location.attributes.has_key("line"):
                        occurrences.append("%s:%i" % (
                            location.attributes["filename"].value,
                            int(location.attributes["line"].value)))
                    elif STRICT:
                        raise LinguistParseError("Malformed 'location' element")

                pluralized = False
                if message.attributes.has_key("numerus") and \
                    message.attributes['numerus'].value=='yes':
                    pluralized = True

                source = _getElementByTagName(message, "source")
                try:
                    translation = _getElementByTagName(message, "translation")
                except LinguistParseError:
                    translation = None
                try:
                    ec_node = _getElementByTagName(message, "extracomment")
                    extracomment = _getText(ec_node.childNodes)
                except LinguistParseError, e:
                    extracomment = None

                # <commend> in ts files are also used to distinguish entries,
                # so we append it to the context to make the entry unique
                try:
                    c_node = _getElementByTagName(message, "comment")
                    comment_text = _getText(c_node.childNodes)
                    if comment_text:
                        comment = escape_context([comment_text])
                    else:
                        comment = []
                except LinguistParseError, e:
                    comment = []

                status = None
                if source.firstChild:
                    sourceString = _getText(source.childNodes)
                else:
                    sourceString = None # WTF?

                # Check whether the message is using logical id
                if message.attributes.has_key("id"):
                    sourceStringText = sourceString
                    sourceString = message.attributes['id'].value
                else:
                    sourceStringText = None

                same_nplural = True
                obsolete, fuzzy = False, False
                messages = []

                if is_source:
                    if translation and translation.attributes.has_key("variants") and \
                      translation.attributes['variants'].value == 'yes':
                        logger.error("Source file has unsupported"
                            " variants.")
                        raise LinguistParseError("Qt Linguist variants are"
                            " not yet supported.")

                    # Skip obsolete strings.
                    if translation and translation.attributes.has_key("type"):
                        status = translation.attributes["type"].value.lower()
                        if status == "obsolete":
                            continue

                    translation_text = None
                    if translation:
                        translation_text = _getText(translation.childNodes)
                    messages = [(5, translation_text or sourceStringText or sourceString)]
                    # remove unfinished/obsolete attrs from template
                    if translation and translation.attributes.has_key("type"):
                        status = translation.attributes["type"].value.lower()
                        if status == "unfinished":
                            del translation.attributes["type"]
                    if pluralized:
                        if translation:
                            try:
                                numerusforms = translation.getElementsByTagName('numerusform')
                                messages = []
                                for n,f in enumerate(numerusforms):
                                    if numerusforms[n].attributes.has_key("variants") and \
                                      numerusforms[n].attributes['variants'].value == 'yes':
                                        logger.error("Source file has unsupported"
                                            " variants.")
                                        raise LinguistParseError("Source file"
                                            " could not be imported: Qt Linguist"
                                            " variants are not supported.")
                                for n,f in enumerate(numerusforms):
                                    if numerusforms[n].attributes.has_key("variants") and \
                                      numerusforms[n].attributes['variants'].value == 'yes':
                                        continue
                                for n,f in enumerate(numerusforms):
                                    nf=numerusforms[n]
                                    messages.append((nplural[n], _getText(nf.childNodes)
                                        or sourceStringText or sourceString ))
                            except LinguistParseError, e:
                                pass
                        else:
                            plural_numbers = self.language.get_pluralrules_numbers()
                            for p in plural_numbers:
                                if p != 5:
                                    messages.append((p, sourceStringText or sourceString))

                elif translation and translation.firstChild:
                    # For messages with variants set to 'yes', we skip them
                    # altogether. We can't support variants at the momment...
                    if translation.attributes.has_key("variants") and \
                      translation.attributes['variants'].value == 'yes':
                        continue

                    # Skip obsolete strings.
                    if translation.attributes.has_key("type"):
                        status = translation.attributes["type"].value.lower()
                        if status == "obsolete":
                            continue

                    if translation.attributes.has_key("type"):
                        status = translation.attributes["type"].value.lower()
                        if status == "unfinished" and\
                          not pluralized:
                            suggestion = GenericTranslation(sourceString,
                                _getText(translation.childNodes),
                                context=context_name + comment,
                                occurrences= ";".join(occurrences))
                            self.suggestions.strings.append(suggestion)
                        else:
                            logger.error("Element 'translation' attribute "\
                                "'type' is neither 'unfinished' nor 'obsolete'")

                        continue

                    if not pluralized:
                        messages = [(5, _getText(translation.childNodes))]
                    else:
                        numerusforms = translation.getElementsByTagName('numerusform')
                        try:
                            for n,f  in enumerate(numerusforms):
                                if numerusforms[n].attributes.has_key("variants") and \
                                  numerusforms[n].attributes['variants'].value == 'yes':
                                    raise StopIteration
                        except StopIteration:
                            continue
                        if nplural:
                            nplural_file = len(numerusforms)
                            if len(nplural) != nplural_file:
                                logger.error("Passed plural rules has nplurals=%s"
                                    ", but '%s' file has nplurals=%s. String '%s'"
                                    "skipped." % (nplural, self.filename,
                                     nplural_file, sourceString))
                                same_nplural = False
                        else:
                            same_nplural = False

                        if not same_nplural:
                            # If we're missing plurals, skip them altogether
                            continue

                        for n,f  in enumerate(numerusforms):
                            nf=numerusforms[n]
                            if nf.firstChild:
                                messages.append((nplural[n], _getText(nf.childNodes)))

                    # NB! If <translation> doesn't have type attribute, it means that string is finished

                if sourceString and messages:
                    for msg in messages:
                        self._add_translation_string(
                            sourceString, msg[1],
                            context = context_name + comment, rule=msg[0],
                            occurrences = ";".join(occurrences),
                            pluralized=pluralized, fuzzy=fuzzy,
                            comment=extracomment, obsolete=obsolete)
                i += 1

                if is_source:
                    if sourceString is None:
                        continue
                    if message.attributes.has_key("numerus") and \
                        message.attributes['numerus'].value=='yes' and translation:
                            numerusforms = translation.getElementsByTagName('numerusform')
                            for n,f in enumerate(numerusforms):
                                f.appendChild(doc.createTextNode(
                                        "%(hash)s_pl_%(key)s" %
                                        {
                                            'hash': hash_tag(sourceString,
                                                context_name + comment),
                                            'key': n
                                        }
                                ))
                    else:
                        if not translation:
                            translation = doc.createElement("translation")

                        # Delete all child nodes. This is usefull for xml like
                        # strings (eg html) where the translation text is split
                        # in multiple nodes.
                        translation.childNodes = []

                        translation.appendChild(doc.createTextNode(
                                ("%(hash)s_tr" % {'hash': hash_tag(
                                    sourceString, context_name + comment)})
                        ))
        return doc

    def _generate_template(self, doc):
        # Ugly fix to revert single quotes back to the escaped version
        template_text = doc.toxml().encode('utf-8')
        esc_template_text = re.sub(
            "'(?=(?:(?!>).)*<\/source>)",
            r"&apos;", template_text
        )
        return esc_template_text.encode(self.default_encoding)

