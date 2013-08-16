import urllib2
# -*- coding: utf-8 -*-
import datetime
from lxml import etree


ontem = (datetime.datetime.now()-datetime.timedelta(1)).strftime("%d/%m/%Y")

def tramites():
	lines = []
	url = 'http://www.camara.gov.br/SitCamaraWS/Proposicoes.asmx/ObterProposicaoTramitacaoPorPeriodo?dtInicio='+ontem+'&dtFim='+ontem

	soup = urllib2.urlopen(url)
	soup = etree.parse(soup).getroot()

	proposicoes = []
	for p in soup.findall("proposicao"):
		proposicao = {}
		for campo in p.iterchildren():
			proposicao[campo.tag] = campo.text.strip()
		proposicoes.append(proposicao)

	for p in proposicoes:
		if p['tipoProposicao'] == 'PL':
			url = 'http://www.camara.gov.br/SitCamaraWS/Orgaos.asmx/ObterAndamento?sigla=' + p['tipoProposicao'] + '&numero=' + p['numero'] + '&ano=' + p['ano'] + '&dataIni=' + ontem + '&codOrgao='
			soup = urllib2.urlopen(url)
			soup = etree.parse(soup).getroot()
			try:
				line = 'Voce sabia que o '
				line += p['tipoProposicao'] + p['numero'] + '/' + p['ano'] + ' que '
				line += soup.xpath('ementa')[0].text.lower().replace('.', '')
				line += ' esta ' + soup.xpath('situacao')[0].text.split(' - ')[1].lower() + ' na ' + soup.xpath('situacao')[0].text.split('-')[0]
				lines.append(line)
			except:
				pass
				#print 'erro no ' +  p['tipoProposicao'] + p['numero'] + '/' + p['ano']
	return lines

def presencas():
	url = 'http://www.camara.gov.br/SitCamaraWS/deputados.asmx/ObterDeputados'

	soup = urllib2.urlopen(url)
	soup = etree.parse(soup).getroot()

	deputados = [p.xpath('matricula')[0].text for p in soup.findall('deputado')]

	for d in deputados:
		url = 'http://www.camara.gov.br/SitCamaraWS/sessoesreunioes.asmx/ListarPresencasParlamentar?dataIni=14/07/2013&dataFim=14/08/2013&numMatriculaParlamentar=' + d

		soup = urllib2.urlopen(url)
		soup = etree.parse(soup).getroot()
		total = len(soup.findall('.//frequencia'))
		presenca = 0
		for p in soup.findall('.//frequencia'):
			if p.text == u'Presença':
				presenca += 1
		ausencia = total - presenca
		line = 'Voce sabia que o '
		line += soup.xpath('nomeParlamentar')[0].text
		if ausencia == 0:
			line += ' nao faltou em nenhuma sessao no ultimo mes!'
		elif ausencia == 1:
			line += ' faltou em uma sessao no ultimo mes?'
		else:
			line += ' faltou em ' + str(ausencia) + ' sessoes no ultimo mes?'
		print line

def reunioes_incomplete():
	url = 'http://www.camara.gov.br/SitCamaraWS/Orgaos.asmx/ObterOrgaos'

	soup = urllib2.urlopen(url)
	soup = etree.parse(soup).getroot()

	orgaos = [p.get('id') for p in soup.findall('orgao')]

	for o in orgaos:
		url = 'http://www.camara.gov.br/SitCamaraWS/Orgaos.asmx/ObterPauta?IDOrgao=' + o + '&datIni=14/08/2013&datFim=14/09/2013'

		soup = urllib2.urlopen(url)
		soup = etree.parse(soup).getroot()

		for reuniao in soup.findall('reuniao'):
			line = 'Voce sabia que o '
			line += soup.get('orgao')
			if reuniao.xpath('tipo')[0].text == u'Audiência Pública':
				line += ' vai realizar uma audiencia publica sobre '
				line += reuniao.xpath('objeto')[0].text
				line += ' no dia ' + reuniao.xpath('data')[0].text + ' as ' + reuniao.xpath('horario')[0].text
			print line

print "Getting tramites..."
lines = tramites()
print "Writing tramites!"
log = open('tramites.txt', 'w')
log.write('\n'.join(lines))
log.close()