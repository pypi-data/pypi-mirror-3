create_entity('CWGroup', name=_('narval'))
create_entity('CWUser', login=_('narval'), upassword='narval0')
rql('SET U in_group G WHERE U login "narval", G name "narval"')
rql('SET U in_group G WHERE U login "narval", G name "guests"')
