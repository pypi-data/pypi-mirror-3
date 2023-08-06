"""more/Notebook client

"""


lay = """
       {N  {  %generali_RIGHT
	      indirizzo  - - 
	      cod_cliente  rs:.30 -
	      citta    cap:.5   pv:.2
	   }
           {  %vendite
              settore
              data_prima_vendita
              fatturato_medio
           }

      }
"""

   

l = Layout(lay)
w = l.show()

