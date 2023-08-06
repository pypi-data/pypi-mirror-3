#: E122 E123
rv.update(dict.fromkeys(
          ('qualif_nr', 'reasonComment_en', 'reasonComment_fr',
           'reasonComment_de', 'reasonComment_it'
           ), '?'), "foo", context={
    'alpha': 4, 'beta': 53242234, 'gamma': 17,
})
#: Okay
rv.update(dict.fromkeys(
          ('qualif_nr', 'reasonComment_en', 'reasonComment_fr',
           'reasonComment_de', 'reasonComment_it'),
          '?'), "foo",
          context={'alpha': 4, 'beta': 53242234, 'gamma': 17})

rv.update(dict.fromkeys(
          ('qualif_nr', 'reasonComment_en', 'reasonComment_fr',
           'reasonComment_de', 'reasonComment_it'
           ),
          '?'), "foo", context={
              'alpha': 4,
              'beta': 53242234,
              'gamma': 17,
          })
#: E127
_ipv4_re = re.compile('^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.'
                       '(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.'
                       '(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.'
                       '(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
#
#: E128


def qualify_by_address(self, cr, uid, ids, context=None,
        params_to_check=frozenset(QUALIF_BY_ADDRESS_PARAM)):
    """ This gets called by the web server """
#: E128
print('l.%s\t%s\t%s\t%r' %
    (token[2][0], pos, tokenize.tok_name[token[0]], token[1]))
#:

######

#: E124 E126
# Some projects use 8 chars indentation inside brackets (), {} or [].
part = MIMEBase(
        a.get('mime_type', 'text'),
        a.get('mime_subtype', 'plain'),
)
#:

#
#
