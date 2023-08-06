# -*- coding: utf-8 -*-
import unittest
import datetime

from pyboleto.bank.hsbc import BoletoHsbcComRegistro

class TestBancoHsbcComRegistro(unittest.TestCase):
    def setUp(self):
        d = BoletoHsbcComRegistro()
        d.agencia_cedente = '0141-4'
        d.conta_cedente = '5000252'
        d.data_vencimento = datetime.date(2010, 11, 6)
        d.data_documento = datetime.date(2010, 11, 6)
        d.data_processamento = datetime.date(2010, 11, 6)
        d.valor_documento = 335.85
        d.nosso_numero = '1716057195'
        d.numero_documento = '02'
        self.dados = d

    def test_linha_digitavel(self):
        self.assertEqual(self.dados.linha_digitavel, 
            '39991.71600 57195.001417 50002.520018 1 47780000033585'
        )
    
    def test_codigo_de_barras(self):
        self.assertEqual(self.dados.barcode, 
            '39991477800000335851716057195001415000252001'
        )

    def test_agencia(self):
        self.assertEqual(self.dados.agencia_cedente, '0141-4')

    def test_conta(self):
        self.assertEqual(self.dados.conta_cedente, '5000252')

    def test_dv_nosso_numero(self):
        self.assertEqual(self.dados.dv_nosso_numero, 0)

suite = unittest.TestLoader().loadTestsFromTestCase(TestBancoHsbcComRegistro)

if __name__ == '__main__':
    unittest.main()

