# Sistema de boletos da Peralta Cobranças

Sistema desenvolvido em `Django 5.2` e `Next.JS 15.3.2`

## Instalação
### Back-End
O Back-End foi feito na linguagem Python usando o framework Django. Por isso, é necessário ter o Python instalado na máquina que for rodar o back-end. Isso pode ser feito utilizando Docker para minimizar problemas de conflito de pacotes.

Com o Python instalado, precisamos de um gerenciador de pacotes. O gerenciador utilizado pelo desenvolvedor foi o `pip`.

1. Vá para a pasta `back/`
2. `pip install -r requirements.txt`
    > Instala as dependências do projeto
3. `python manage.py makemigrations`
    > Lê os modelos do banco de dados e gera arquivos de migração
4. `python manage.py migrate`
    > Cria o banco de dados a partir dos arquivos de migração

Para testar se está tudo funcional, execute o comando `python manage.py runserver`. Ele levantará um servidor de testes (apenas para testes!)

### Front-End
O Front-End foi feito na linguagem Typescript, com o framework Next.JS. Para executar projetos com Next.JS na versão utilizada aqui neste projeto, é necessário o Node versão 20. Caso a máquina que vá hospedar o projeto do Front-End já possua um Node em versão diferente, é possível instalar novas versões usando o comando [`nvm`](https://www.freecodecamp.org/news/node-version-manager-nvm-install-guide/)

Também é necessário um gerenciador de pacotes de Javascript. O gerenciador usado pelo desenvolvedor foi o `npm`.

1. Vá para a pasta `front/`
2. `npm install`
    > Instala as dependências do projeto
3. `npm build`
    > Compila o projeto, gerando uma versão de produção

Para testar se deu tudo certo, execute `npm run dev`. De maneira similar ao back, esse comando levanta um servidor de testes (apenas testes!).


## Autenticação
Este projeto utiliza JWT para autenticação. Usuários e sistemas que queiram consumir a API devem possuir um token JWT. Mas atenção: Por segurança, os tokens JWT gerados para usuários possuem menos permissões que tokens gerados para sistemas!!!!

Para gerar um token para um sistema, basta utilizar o seguinte comando dentro da pasta `back/`:

`python manage.py token nome_do_sistema_que_utilizara_a_api`

Esse comando retornará **dois** tokens: Um de acesso e outro de _refresh_. Para chamadas de API comuns, utilize o token de **acesso**. Quando ele expirar, você vai chamar o endpoint de _refresh_ passando o token de **refresh**. Mais sobre isso [aqui](https://auth0.com/blog/pt-refresh-tokens-what-are-they-and-when-to-use-them/).


## Documentação técnica da API
A documentação da API pode ser acessada no link `www.dominiodosistema.com/api/docs`.

**Todos** os endpoints possuem documentação do formato de dados de entrada e saída.