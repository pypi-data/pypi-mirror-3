import sparql, cairo, CairoPlot

querytemplate = """
PREFIX txn: <http://lod.taxonconcept.org/ontology/txn.owl#>
PREFIX e: <http://eunis.eea.europa.eu/rdf/species-schema.rdf#>

SELECT ?eol ?code
WHERE {
 ?especies a e:SpeciesSynonym;
          e:speciesCode ?code;
          e:sameSynonymITIS ?eitis.
 ?tspecies txn:hasITIS ?eitis;
           txn:hasEOL ?eol
}
"""
endpoint = "http://semantic.eea.europa.eu/sparql"
s = sparql.Service(endpoint)

result = s.query(querytemplate)
for row in result.fetchone():
#   print """INSERT INTO chm62edt_nature_object_links SELECT ID_NATURE_OBJECT, 'http://www.eol.org/pages/%s/overview','Encyclopedia of Life:%s' from chm62edt_species WHERE ID_SPECIES = %s;""" % (str(row[0]), str(row[0]), str(row[1]))
    print """INSERT INTO chm62edt_nature_object_attributes SELECT ID_NATURE_OBJECT, '_sameSynonymEOL','%s','','' from chm62edt_species WHERE ID_SPECIES = %s;""" % (str(row[0]), str(row[1]))


