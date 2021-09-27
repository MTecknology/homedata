" temp for python
"set expandtab
"set tabstop=4

""
" Syntax Stuff
""

" Wrap RST at 80 chars
autocmd BufEnter,BufRead *.rst syn on | set syntax=rst | set tw=80 | set wrap

" Salt States
"autocmd BufEnter,BufRead *.sls syn on | set syntax=yaml
set nocompatible
filetype plugin indent on

""
" Basic Options
""

set encoding=utf-8
set modelines=0
set autoindent
set showmode
set showcmd
set hidden
set cursorline
set ttyfast
set ruler
set backspace=indent,eol,start
set number
set mouse=
"set relativenumber
set laststatus=2
set history=1000
set undofile
set undoreload=1000
"set list
set shell=/bin/bash
set lazyredraw
set showbreak=⇲
set splitbelow
set splitright
set autowrite
set autoread
set title
set scrolloff=7
syntax on

""
" Backups
" mkdir -p ~/.vim/tmp/{undo,backup,swap}
""

set undodir=~/.vim/tmp/undo//     " undo files
set backupdir=~/.vim/tmp/backup// " backups
set directory=~/.vim/tmp/swap//   " swap files
set backup                        " enable backups

""
" Irritating Keys
""

noremap  <F1> <nop>
inoremap <F1> <nop>
nnoremap K    <nop>
inoremap #    X<BS>#

""
" To Become A Pro
""

"inoremap <Up>    <nop>
"inoremap <Down>  <nop>
"inoremap <Left>  <nop>
"inoremap <Right> <nop>
"noremap  <Up>    <nop>
"noremap  <Down>  <nop>
"noremap  <Left>  <nop>
"noremap  <Right> <nop>
