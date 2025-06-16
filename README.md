# Personal Trainer Schedule Management App

## Descrição

Este é um aplicativo desenvolvido com Streamlit para ajudar personal trainers a gerenciar suas agendas e cadastros de alunos. O aplicativo possui três páginas principais:

1. **Agenda**: Exibe a agenda do mês atual em formato de calendário, com cada coluna representando um dia da semana. Mostra quantos alunos estão agendados e se há vagas disponíveis.
2. **Cadastro de Alunos**: Permite o cadastro de novos alunos com 10 campos principais e exibe o banco de dados de alunos.
3. **Contato e Versão**: Fornece informações de contato e a versão do aplicativo.

## Funcionalidades

- **Visualização da Agenda**: A agenda é exibida em formato de calendário, facilitando a visualização dos horários disponíveis e agendamentos.
- **Cadastro de Alunos**: Formulário de cadastro de alunos com campos para nome, idade, gênero, email, telefone, endereço, contato de emergência, condições médicas, objetivos e informações adicionais.
- **Operações CRUD**: Permite criar, ler, atualizar e deletar registros de alunos no banco de dados.
- **Banco de Dados em CSV**: O banco de dados de alunos é armazenado em um arquivo CSV, facilitando a persistência e a manipulação dos dados.

## Desafios

- **Gerenciamento de Agenda**: Personal trainers frequentemente enfrentam dificuldades para gerenciar suas agendas devido ao grande número de alunos e a necessidade de remarcações frequentes.
- **Organização dos Dados dos Alunos**: Manter um registro organizado e atualizado dos dados dos alunos pode ser desafiador sem uma ferramenta adequada.

## Soluções

- **Automatização da Agenda**: O aplicativo automatiza a visualização da agenda, tornando mais fácil para o personal trainer ver os horários disponíveis e agendamentos.
- **Cadastro e Gerenciamento de Alunos**: O formulário de cadastro e as operações CRUD permitem que o personal trainer mantenha um banco de dados organizado e atualizado dos alunos.
- **Facilidade de Uso**: A interface do aplicativo é simples e intuitiva, facilitando o uso diário pelo personal trainer.

## Instalação

Para executar o aplicativo, siga os passos abaixo:

1. Clone este repositório:
    ```bash
    git clone https://github.com/seu-usuario/seu-repositorio.git
    ```

2. Navegue até o diretório do projeto:
    ```bash
    cd seu-repositorio
    ```

3. Instale as dependências:
    ```bash
    pip install streamlit pandas
    ```

4. Execute o aplicativo:
    ```bash
    streamlit run app.py
    ```

## Contato

Para qualquer dúvida, entre em contato: exemplo@exemplo.com

## Versão

Versão do Aplicativo: 1.0.0
