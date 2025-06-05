def clausura_epsilon(estado, transiciones):
    clausura = {estado}
    pila = [estado]
    
    while pila:
        actual = pila.pop()
        if actual in transiciones and '' in transiciones[actual]:
            for siguiente_estado in transiciones[actual]['']:
                if siguiente_estado not in clausura:
                    clausura.add(siguiente_estado)
                    pila.append(siguiente_estado)
    
    return clausura

def clausura_epsilon_conjunto(estados, transiciones):
    clausura = set()
    for estado in estados:
        clausura.update(clausura_epsilon(estado, transiciones))
    return clausura

def mover(estados, simbolo, transiciones):
    resultado = set()
    for estado in estados:
        if estado in transiciones and simbolo in transiciones[estado]:
            resultado.update(transiciones[estado][simbolo])
    return resultado

def convertir_afnd_a_afd(estados, alfabeto, transiciones, estado_inicial, estados_finales):
    clausura_inicial = frozenset(clausura_epsilon(estado_inicial, transiciones))
    
    estados_afd = [clausura_inicial]
    transiciones_afd = {}
    estados_no_marcados = [clausura_inicial]
    
    while estados_no_marcados:
        estado_actual = estados_no_marcados.pop(0)
        transiciones_afd[estado_actual] = {}
        
        for simbolo in alfabeto:
            resultado_movimiento = mover(estado_actual, simbolo, transiciones)
            siguiente_estado = frozenset(clausura_epsilon_conjunto(resultado_movimiento, transiciones))
            
            if siguiente_estado:
                transiciones_afd[estado_actual][simbolo] = siguiente_estado
                
                if siguiente_estado not in estados_afd:
                    estados_afd.append(siguiente_estado)
                    estados_no_marcados.append(siguiente_estado)
    
    estados_finales_afd = [
        estado for estado in estados_afd 
        if any(final in estado for final in estados_finales)
    ]
    
    mapeo_estados = {estado: f"q{i}" for i, estado in enumerate(estados_afd)}
    
    transiciones_renombradas = {}
    for estado_antiguo, trans in transiciones_afd.items():
        nuevo_estado = mapeo_estados[estado_antiguo]
        transiciones_renombradas[nuevo_estado] = {}
        
        for simbolo, siguiente_estado in trans.items():
            transiciones_renombradas[nuevo_estado][simbolo] = mapeo_estados[siguiente_estado]
    
    estados_finales_renombrados = [mapeo_estados[estado] for estado in estados_finales_afd]
    estado_inicial_renombrado = mapeo_estados[clausura_inicial]
    
    return (
        list(mapeo_estados.values()),
        list(alfabeto),
        transiciones_renombradas,
        estado_inicial_renombrado,
        estados_finales_renombrados
    )

def imprimir_tabla_transiciones(estados, alfabeto, transiciones):
    """Imprime una tabla de transiciones formateada."""
    encabezado = "Estado"
    for simbolo in alfabeto:
        encabezado += f" | {simbolo:^10}"
    
    print(encabezado)
    print("-" * len(encabezado))
    
    for estado in sorted(estados):
        fila = f"{estado:6}"
        for simbolo in alfabeto:
            simbolo_mostrar = simbolo if simbolo != '' else 'ε'
            if estado in transiciones and simbolo_mostrar in transiciones[estado]:
                siguientes_estados = transiciones[estado][simbolo_mostrar]
                if isinstance(siguientes_estados, list) or isinstance(siguientes_estados, set):
                    fila += f" | {','.join(siguientes_estados):^10}"
                else:
                    fila += f" | {siguientes_estados:^10}"
            else:
                fila += f" | {'--':^10}"
        print(fila)

def visualizar_automata(estados, alfabeto, transiciones, estado_inicial, estados_finales, nombre_archivo="automata"):
    """Crea una visualización gráfica del autómata usando Graphviz."""
    try:
        from graphviz import Digraph
    except ImportError:
        print("Para visualizar el autómata, es necesario instalar graphviz:")
        print("pip install graphviz")
        print("También necesitas instalar el software Graphviz: https://graphviz.org/download/")
        return None

    dot = Digraph(comment='Autómata Finito Determinista')
    dot.attr(rankdir='LR') 

    dot.attr('node', shape='none', height='0', width='0')
    dot.node('start', '')
    
    for estado in estados:
        if estado in estados_finales:
            dot.attr('node', shape='doublecircle')
        else:
            dot.attr('node', shape='circle')
        dot.node(estado)
    
    dot.edge('start', estado_inicial)
    
    for origen, trans in transiciones.items():
        for simbolo, destino in trans.items():
            if isinstance(destino, (list, set, frozenset)):
                for d in destino:
                    dot.edge(origen, d, label=simbolo)
            else:
                dot.edge(origen, destino, label=simbolo)
    
    try:
        dot.render(nombre_archivo, format='png', cleanup=True)
        print(f"Imagen guardada como {nombre_archivo}.png")
        return dot
    except Exception as e:
        print(f"Error al generar la visualización: {e}")
        return None

def principal():
    print("=============================================================")
    print("        Conversión de AFND con transiciones vacías a AFD     ")
    print("=============================================================")
    
    try:
        n_estados = int(input("\nIngrese el número de estados del AFND: "))
        if n_estados <= 0:
            print("El número de estados debe ser positivo.")
            return
    except ValueError:
        print("Por favor ingrese un número válido.")
        return
    
    estados = [f"q{i}" for i in range(n_estados)]
    print(f"Estados: {estados}")
    
    entrada_alfabeto = input("\nIngrese los símbolos del alfabeto separados por coma (sin incluir épsilon): ")
    alfabeto = [simbolo.strip() for simbolo in entrada_alfabeto.split(',') if simbolo.strip()]
    
    if not alfabeto:
        print("El alfabeto no puede estar vacío.")
        return
    print(f"Alfabeto: {alfabeto}")
    
    transiciones = {}
    print("\nIngreso de transiciones:")
    print("Para cada estado y cada símbolo, ingrese los estados destino separados por coma.")
    print("Si no hay transición, presione Enter sin escribir nada.\n")
    
    for estado in estados:
        transiciones[estado] = {}

        for simbolo in alfabeto:
            entrada_transicion = input(f"Transición de {estado} con símbolo '{simbolo}': ")
            if entrada_transicion.strip():
                destinos = [t.strip() for t in entrada_transicion.split(',') if t.strip()]
                if destinos:
                    transiciones[estado][simbolo] = destinos
        
        entrada_epsilon = input(f"Transición de {estado} con épsilon (e): ")
        if entrada_epsilon.strip():
            destinos = [t.strip() for t in entrada_epsilon.split(',') if t.strip()]
            if destinos:
                transiciones[estado][''] = destinos
    
    while True:
        estado_inicial = input("\nIngrese el estado inicial: ")
        if estado_inicial in estados:
            break
        print("El estado inicial debe estar entre los estados definidos.")

    while True:
        entrada_finales = input("Ingrese los estados finales separados por coma: ")
        estados_finales = [estado.strip() for estado in entrada_finales.split(',') if estado.strip()]
        
        if all(estado in estados for estado in estados_finales) and estados_finales:
            break
        print("Todos los estados finales deben estar entre los estados definidos.")
    
    print("\nAFND con transiciones vacías:")
    print(f"Estados: {estados}")
    print(f"Alfabeto: {alfabeto}")
    print(f"Estado inicial: {estado_inicial}")
    print(f"Estados finales: {estados_finales}")
    
    transiciones_mostrar = {}
    for estado, trans in transiciones.items():
        transiciones_mostrar[estado] = {}
        for simbolo, destinos in trans.items():
            simbolo_mostrar = simbolo if simbolo else 'ε'
            transiciones_mostrar[estado][simbolo_mostrar] = destinos
    
    print("\nTabla de transiciones del AFND:")
    imprimir_tabla_transiciones(estados, alfabeto + ['ε'], transiciones_mostrar)
 
    estados_afd, alfabeto_afd, transiciones_afd, inicial_afd, finales_afd = convertir_afnd_a_afd(
        estados, alfabeto, transiciones, estado_inicial, estados_finales
    )
    
    print("\nAFD Resultante:")
    print(f"Estados: {estados_afd}")
    print(f"Alfabeto: {alfabeto_afd}")
    print(f"Estado inicial: {inicial_afd}")
    print(f"Estados finales: {finales_afd}")
    print("\nTabla de transiciones del AFD:")
    imprimir_tabla_transiciones(estados_afd, alfabeto_afd, transiciones_afd)
    
    # Visualizar el autómata
    visualizar = input("\n¿Desea visualizar gráficamente el autómata? (s/n): ").lower()
    if visualizar == 's' or visualizar == 'si':
        nombre_archivo = input("Ingrese un nombre para el archivo de visualización (o presione Enter para 'automata'): ")
        if not nombre_archivo.strip():
            nombre_archivo = "automata"
        visualizar_automata(estados_afd, alfabeto_afd, transiciones_afd, inicial_afd, finales_afd, nombre_archivo)
        print(f"\nLa imagen del autómata ha sido generada. Puede verla en el archivo {nombre_archivo}.png")

if __name__ == "__main__":
    principal()