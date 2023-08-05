"""Comentario de módulo"""

def print_listaRecursiva(lista):
    """Comentario de función"""
    for i in lista:
        if isinstance(i,list):
            print_listaRecursiva(i)
        else:
            print(i)

