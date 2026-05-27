def sugerir_especialidade(relato_paciente: str) -> str:
    """
    Analisa palavras-chave no relato do paciente para sugerir a especialidade ideal.
    (Simulação de IA em formato de regras para MVP gratuito).
    """
    relato = relato_paciente.lower()
    
    regras = {
        "Fisioterapeuta": ["dor", "movimento", "coluna", "fratura", "reabilitação", "cirurgia ortopédica", "andar"],
        "Enfermeiro": ["curativo", "medicação na veia", "sonda", "pós-operatório complexo", "dreno"],
        "Técnico de Enfermagem": ["banho", "medicação oral", "pressão", "glicemia", "higiene"],
        "Nutricionista": ["dieta", "alimentação", "perda de peso", "diabetes", "sonda alimentar", "nutrição"],
        "Cuidador": ["companhia", "alzheimer", "idoso", "ajuda diária", "passeio", "lembrar remédios"],
        "Médico": ["diagnóstico", "receita", "exames", "dor aguda", "urgência", "falta de ar"]
    }
    
    pontuacoes = {especialidade: 0 for especialidade in regras}
    
    # Conta as palavras-chave encontradas
    for especialidade, palavras in regras.items():
        for palavra in palavras:
            if palavra in relato:
                pontuacoes[especialidade] += 1
                
    # Encontra a especialidade com maior pontuação
    especialidade_sugerida = max(pontuacoes, key=pontuacoes.get)
    
    # Se não encontrar nenhuma palavra-chave, sugere um Cuidador ou Médico para triagem
    if pontuacoes[especialidade_sugerida] == 0:
        return "Clínico Geral para Avaliação"
        
    return especialidade_sugerida