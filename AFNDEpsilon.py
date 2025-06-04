class AFNDEpsilon:
    def __init__(self):
        self.estados = set()
        self.alfabeto = set()
        self.transiciones = {}
        self.estado_inicial = None
        self.estados_aceptacion = set()

    def agregar_transicion(self, estado, simbolo, estados_destino):
        if (estado, simbolo) not in self.transiciones:
            self.transiciones[(estado, simbolo)] = set()
        self.transiciones[(estado, simbolo)].update(estados_destino)

    def obtener_transiciones(self, estado, simbolo):
        return self.transiciones.get((estado, simbolo), set())