# Sistema de boletos da Peralta Cobranças

Sistema desenvolvido em `Django 5.2` e `Next.JS 15.3.2`

## Instalação

> Observação: embora apareça depois, a etapa de configurar os arquivos .env, so for utilizá-los, deve ocorrer ANTES da etapa de Instalação, pois esta copia os arquivos para o container e alterações neles depois da cópia não surtem efeito

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


## Configuração
Tanto o Back-End quanto o Front-End lêem variáveis de configuração do ambiente onde estão hospedados.

### Back-End
1. ENV: Pode ser 'prod' ou 'dev'. Define o ambiente atual
2. SMS_CODE_EXPIRATION_SECONDS: Tempo de expiração de um código de Login. Em segundos
3. SMS_API_ENDPOINT: Link da API de SMS sendo utilizada
4. SMS_API_KEY: Chave de autenticação da API de SMS

5. USING_AWS: Se vai ou não utilizar AWS. Se for False, não precisa configurar as chaves abaixo relativas a AWS
6. AWS_ACCESS_KEY_ID: ID da chave de acesso da AWS
7. AWS_SECRET_ACCESS_KEY: Chave secreta de acesso da AWS
8. AWS_STORAGE_BUCKET_NAME: Nome do bucket de armazenamento na AWS S3

9. AWS_S3_ENDPOINT_URL: URL do endpoint do S3.
10. AWS_S3_REGION_NAME: Região do bucket S3. O padrão é `us-east-1`.
11. AWS_S3_SIGNATURE_VERSION: Versão da assinatura do S3. O padrão é `s3v4`.
12. AWS_S3_FILE_OVERWRITE: Define se os arquivos enviados para o S3 devem sobrescrever os arquivos com o mesmo nome. O padrão é `False`.
13. AWS_DEFAULT_ACL: Define a ACL padrão para os arquivos enviados ao S3. O padrão é `None`, o que significa que não há ACL definida (recomendado).

### Front-End
1. NEXT_PUBLIC_API_URL: Link de onde a API está hospedada
2. NEXT_PUBLIC_WPP_NUMBER: Número de Whatsapp para onde os usuários serão redirecionados quando clicarem nos botões de contato por Whatsapp


## Autenticação
Este projeto utiliza JWT para autenticação. Usuários e sistemas que queiram consumir a API devem possuir um token JWT. Mas atenção: Por segurança, os tokens JWT gerados para usuários possuem menos permissões que tokens gerados para sistemas!!!!

Para gerar um token para um sistema, basta utilizar o seguinte comando dentro da pasta `back/`:

`python manage.py token nome_do_sistema_que_utilizara_a_api`

Esse comando retornará **dois** tokens: Um de acesso e outro de _refresh_. Para chamadas de API comuns, utilize o token de **acesso**. Quando ele expirar, você vai chamar o endpoint de _refresh_ passando o token de **refresh**. Mais sobre isso [aqui](https://auth0.com/blog/pt-refresh-tokens-what-are-they-and-when-to-use-them/).


## Documentação técnica da API
A documentação da API pode ser acessada no link `www.dominiodosistema.com/api/docs`.

**Todos** os endpoints possuem documentação do formato de dados de entrada e saída.