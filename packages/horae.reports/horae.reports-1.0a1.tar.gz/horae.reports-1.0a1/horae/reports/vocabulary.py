from zope.schema import vocabulary

from horae.reports import interfaces


def reports_vocabulary_factory(context):
    """ A vocabulary of all available reports registered as
        **horae.reports.vocabulary.reports**
    """
    reports = interfaces.IReports(context)
    terms = []
    for report in reports.objects():
        terms.append(vocabulary.SimpleTerm(report, report.id, report.name))
    return vocabulary.SimpleVocabulary(terms)
vocabulary.getVocabularyRegistry().register('horae.reports.vocabulary.reports', reports_vocabulary_factory)
