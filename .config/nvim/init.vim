" ----- Basic settings -----
" Set the leader key to space
let mapleader=" "
" Enable syntax highlighting
syntax on
" Set the spell check language to English
set spelllang=en_au
" Enable standard and relative line numbers
set number
set relativenumber
" Preserves buffers when switching them
set hidden
" Disable all bells
set belloff=all
" Use tabs of equivalent 4 spaces for display
set autoindent noexpandtab tabstop=4 shiftwidth=4
" Disable mode display, made unnecessary with airline
set noshowmode
" Keep the cursor from scrolling to the top and bottom
set scrolloff=8
" Enable the mouse
set mouse=a
" Remove trailing whitespace on save
autocmd BufWritePre * %s/\s\+$//e
" Ignore default python indentation settings
let g:python_recommended_style = 0

" ----- Plugin management -----
call plug#begin('~/.config/nvim/plugged')
" Colour schemes
Plug 'crusoexia/vim-monokai'
Plug 'dylanaraps/wal.vim'
Plug 'gruvbox-community/gruvbox'

" Better status bar and themes for it
Plug 'vim-airline/vim-airline'
Plug 'vim-airline/vim-airline-themes'

" Workflow plugins
Plug 'haya14busa/incsearch.vim'
Plug 'tpope/vim-commentary'
Plug 'tpope/vim-surround'
Plug 'rstacruz/vim-closer'
Plug 'ervandew/supertab'
call plug#end()

" ----- Colour scheme settings -----
" Change the colour schemes for vim and airline
colorscheme monokai
let g:airline_theme="badwolf"
" Disable background colour of the theme
highlight Normal guibg=NONE ctermbg=NONE
highlight LineNr ctermbg=NONE
highlight CursorLineNr ctermbg=NONE

" ----- Plugin specific settings -----
" Tab complete in descending order
let g:SuperTabDefaultCompletionType = "<c-n>"
" Configure incsearch and disable persistent highlighting
set hlsearch
let g:incsearch#auto_nohlsearch = 1
map /  <Plug>(incsearch-forward)
map ?  <Plug>(incsearch-backward)
map g/ <Plug>(incsearch-stay)
map n  <Plug>(incsearch-nohl-n)
map N  <Plug>(incsearch-nohl-N)
map *  <Plug>(incsearch-nohl-*)
map #  <Plug>(incsearch-nohl-#)
map g* <Plug>(incsearch-nohl-g*)
map g# <Plug>(incsearch-nohl-g#)

" ----- Remap settings -----
" Delete without copying visual block
vnoremap <leader>p "_dP
" Keep visual block highlighted after indent
vnoremap < <gv
vnoremap > >gv
" Allows for adding blank lines without entering insert mode
nnoremap <leader>o o<Esc>k
nnoremap <leader>O O<Esc>j
" Remap F6 to toggle spellcheck
nnoremap <silent> <F6> :set spell!<cr>
inoremap <silent> <F6> <C-O>:set spell!<cr>
" Remap F5 to insert a timestamp
nnoremap <F5> "=strftime("%I:%M %p %a %d/%m/%Y")<CR>p
inoremap <F5> <C-R>=strftime("%I:%M %p %a %d/%m/%Y")<CR>
