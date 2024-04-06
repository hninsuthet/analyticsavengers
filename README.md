# IS483

This template should help get you started developing with Vue 3 in Vite.

## Recommended IDE Setup

[VSCode](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur) + [TypeScript Vue Plugin (Volar)](https://marketplace.visualstudio.com/items?itemName=Vue.vscode-typescript-vue-plugin).

## Customize configuration

See [Vite Configuration Reference](https://vitejs.dev/config/).

## Project Setup

### Python Flask

1. Start by creating a [Python Flask Environment](https://flask.palletsprojects.com/en/3.0.x/installation/)

For macOS/Linux

```sh
$ cd "Web Development"
$ python3 -m venv .venv
```

For Windows

```sh
> cd "Web Development"
> py -3 -m venv .venv
```

2. Activating the environment

For macOS/Linux

```sh
$ . .venv/bin/activate
```

For Windows

```sh
> .venv\Scripts\activate

# resolve issue if there is the execution policy set on your system
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

3. Navigate to `server` folder and type:

```sh
pip install -r requirements.txt
```

To run website, open three terminals for `client`, `BE_Controller server` and `BE_PA2 server`

### client (Vue)

1. Navigate to `client` folder and type:

```sh
npm install #if npm is not installed yet
npm install d3 #install d3
npm install vue-loading-overlay # install loading indicator
npm run dev

```

### BE Controller server (Python flask)

1. Navigate to `BE_Controller` folder and type:

```sh
python app.py

pip install --upgrade flask werkzeug #ensure to use latest version of flask
```

### BE PA2 server (Python flask)

1. Navigate to `BE_PA2` folder and type:

```sh
python app.py

pip install --upgrade flask werkzeug #ensure to use latest version of flask
```