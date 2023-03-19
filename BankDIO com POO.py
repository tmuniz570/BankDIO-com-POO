from abc import ABC, abstractproperty, abstractclassmethod
from datetime import datetime


class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf

class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        excedeu_saldo = valor >= self.saldo

        if excedeu_saldo:
            print("Saldo insuficiente!")
        elif valor > 0:
            self._saldo -= valor
            print(f"Saque realizado no valor de {valor}.")
            return True
        else:
            print("Valor invalido!")

        return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print(f"Deposito de {valor} realizado!")
            return True
        else:
            print("Valor invalido!")
            return False

class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__])

        excedeu_limite = valor > self.limite
        excedeu_saques = numero_saques >= self.limite_saques

        if excedeu_limite:
            print("Valor do saque acima do limite!")
        elif excedeu_saques:
            print("Limite de saques excedido nesta conta!")
        else:
            return super().sacar(valor)
        return False

    def __str__(self):
        return f"""
        Ag:\t{self.agencia}
        C/c:\t{self.numero}
        Titular:\t{self.cliente.nome}"""

class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                #"data": datetime.now().strftime("%d/%m/%Y %H:%M:%s")
            }
        )

class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass
    @abstractclassmethod
    def registrar(self, conta):
        pass

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        if conta.sacar(self.valor):
            conta.historico.adicionar_transacao(self)

class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        if conta.depositar(self.valor):
            conta.historico.adicionar_transacao(self)

def menu():
    print("""
    Banco DIO
    [d] Depositar
    [s] Sacar
    [e] Extrato
    [nu] Novo Usuario
    [nc] Nova Conta
    [lc] Listar Contas
    [q] Sair

    => """)
    return input()

def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None

def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("Este cliente nao possui conta cadastrada!")
        return
    # adicionar escolha da conta a ser utilizada
    return cliente.contas[0]

def depositar(clientes):
    cpf = input("Digite o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("Cliente nao cadastrado!")
        return

    valor = float(input("Digite o valor para depositar: "))
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)

def sacar(clientes):
    cpf = input("Digite o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("Cliente nao cadastrado!")
        return

    valor = float(input("Digite o valor para sacar: "))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)

def exibir_extrato(clientes):
    cpf = input("Digite o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("Cliente nao cadastrado!")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    print("==========EXTRATO==========")
    transacoes = conta.historico.transacoes

    extrato = ""
    if not transacoes:
        extrato = "Sem movimentacoes na conta!"
    else:
        for transacao in transacoes:
            extrato += f"\n{transacao['tipo']}:\n\tR${transacao['valor']:.2f}"

    print(extrato)
    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")
    print("===========================")

def criar_cliente(clientes):
    cpf = input("Digite o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("Cliente ja cadastrado!")
        return

    nome = input("Digite o nome: ")
    data_nascimento = input("Digite a data de nascimento: ")
    endereco = input("Digite o endereco: ")

    cliente = PessoaFisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco)

    clientes.append(cliente)

    print("Cliente adicionado!")

def criar_conta(clientes, contas):
    cpf = input("Digite o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("Cliente nao cadastrado!")
        return
    numero_conta = len(contas) + 1
    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)

    print("Conta adicionada!")

def listar_contas(contas):
    for conta in contas:
        print("=" * 20)
        print(conta)

clientes = []
contas = []

while True:
    opcao = menu()

    if opcao == "d":
        depositar(clientes)
    elif opcao == "s":
        sacar(clientes)
    elif opcao == "e":
        exibir_extrato(clientes)
    elif opcao == "nu":
        criar_cliente(clientes)
    elif opcao == "nc":
        criar_conta(clientes, contas)
    elif opcao == "lc":
        listar_contas(contas)
    elif opcao == "q":
        break
    else:
        print("Opcao invalida! Tente novamente!")