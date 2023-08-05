domain=rendezvous
i18ndude rebuild-pot --pot locales/$domain.pot --create $domain --merge i18n/generated.pot .
i18ndude sync --pot locales/$domain.pot locales/*/LC_MESSAGES/$domain.po

i18ndude rebuild-pot --pot locales/plone.pot --create plone profiles
i18ndude sync --pot locales/plone.pot locales/*/LC_MESSAGES/plone.po
