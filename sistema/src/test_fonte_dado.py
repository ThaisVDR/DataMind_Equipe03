"""Verificacoes de conversao com casos que nao podem virar zero/duplicacao silenciosa."""
import unittest
from decimal import Decimal
from fonte_dado_etl import number,norm,transform_row

class ConversionTests(unittest.TestCase):
    def test_missing_and_decimal_comma(self):
        self.assertIsNone(number('SC'))
        self.assertIsNone(number(None))
        self.assertEqual(number('1.234,50'),Decimal('1234.50'))
        with self.assertRaises(ValueError):number('1.5',integer=True)
        with self.assertRaises(ValueError):number('SC',required=True)

    def test_header_footnotes(self):
        self.assertEqual(norm(' Código do Curso** '),'codigo_do_curso')
        self.assertEqual(norm('Nº  de Concluintes Participantes'),'no_de_concluintes_participantes')

    def test_ibge_zero_missing_and_grain(self):
        item={'family':'ibge','version':'test','period':'9514'}
        row={'tabela':'9514','variavel_id':'93','variavel_nome':'Populacao','unidade':'Pessoas',
             'nivel_geografico':'N6','localidade_id':'5100102','localidade_nome':'Acorizal',
             'periodo':'2022','valor':'-','class_2_categoria_id':'6794','class_2_categoria_nome':'Total'}
        zero=transform_row(item,row)
        missing=transform_row(item,{**row,'valor':'...'})
        self.assertEqual(zero[10],Decimal(0))
        self.assertEqual(zero[12],'zero_absoluto')
        self.assertIsNone(missing[10])
        self.assertEqual(missing[12],'nao_disponivel')
        self.assertEqual(zero[1],missing[1])
        self.assertNotEqual(zero[1],transform_row(item,{**row,'class_2_categoria_id':'4'})[1])
        with self.assertRaises(ValueError):transform_row(item,{**row,'localidade_id':'5300108'})

if __name__=='__main__':unittest.main()
