GABARITOS = {
    1: "abcedaecdadeaaeadced", 
    2: "abcedaecdadeaaeadced",  
    3: "abcedaecdadeaaeadced",
    4: "abcedaecdadeaaeadced",
    5: "abcedaecdadeaaeadced",
    6: "abcedaecdadeaaeadced",
    7: "abcedaecdadeaaeadced",
}

def calcular_pontuacao(leitura, gabarito):
    if not leitura or not gabarito:
        return 0
    return sum(1 for l, g in zip(leitura, gabarito) if l == g)