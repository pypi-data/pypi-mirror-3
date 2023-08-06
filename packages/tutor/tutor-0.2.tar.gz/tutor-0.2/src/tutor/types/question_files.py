#-*- coding: utf8 -*-
'''Contents for the text files in the question objects'''

AUTHOR = u'Fulano da Silva'
TITLE = u'Questão exemplo: soma de dois números'

#===============================================================================
# src/namespace.py file
#===============================================================================
NAMESPACE_EXAMPLE = r'''# This is a sample script file. The variables defined in this file will be used
# to fill in the missing template parameters.
# 
# The present script chooses 2 integers randomly and computes their sum.
# A few wrong answers (distractors) are also calculated, and may correspond to
# other mathematical operations. 

# We may begin importing the functions in the tutor.scripts module.
from tutor.scripts import *

# The oneof() function picks up one of its arguments or, if it is called with a 
# single iterable argument, it picks up one of its items.
# The display_block() context manager is useful for debugging as it prints the 
# values of the new variables created within it

with display_block('Input and answer'):
    intA = oneof(-1, 1) * oneof(range(1, 10))
    intB = oneof(range(1, 10))
    sumAB = intA + intB

# Here we compute a few distractors
with display_block('Distractors'):
    dis1 = intA - intB
    dis2 = intB - intA
    dis3 = - sumAB
    dis4 = (intA + intB) / 2
'''

NAMESPACE = r'''
# Put your imports in here
from tutor.scripts import *

# Uncomment in order to enable symbolic computation with sympy or maple
# from tutor.plugins.sympy import * 
# from tutor.plugins.maple import *

# The variables you define in the script will be accessible from 
# templates. You can also use the display_vars function to print the new values
# to the screen in order to aid with debugging:
with display_vars('Parameters'):
    a = randint(1, 10)
    b = randint(1, 10)
    sum_ab = a + b
'''


#===============================================================================
# src/main.tex
#===============================================================================
MAIN_TEX = r'''\documentclass[brazil]{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{pytutor}
\usepackage{babel}

\begin{document}

\title{%(title)s}
\author{%(author)s}
\date{12/12/2012}
\maketitle

\begin{introtext}
Esta é uma questão exemplo. Normalmente as questões iniciam com um texto 
introdutório que deve ser marcado em latex com o ambiente \texttt{intro}. 
Lembre-se que no LyX é possível adicionar comandos \LaTeX\ arbitrários utilizando
as caixas de código \TeX\ (ctrl+L). As marcações definidas pelo sistema tutor 
estão definidas no pacote \texttt{pytutor} e portanto o documento deve incluir 
uma cláusula \texttt{\textbackslash{}usepackage\{pytutor\}} no preâmbulo.
Este arquivo de exemplo já contêm a estrutura básica esperada para uma questão 
e compila normalmente se o sistema \texttt{pytutor} estiver corretamente 
instalado.
\end{introtext}

\begin{multiplechoice} 
Em uma questão normal, o texto acima seria
relevante para resolução da mesma. Nesta questão de exemplo, ele não
é. O ambiente \texttt{intro} sequer é necessário já que o comando
principal da questão pode ser incluído diretamente junto com o ambiente
que define o tipo de quetão a ser abordada (e.g. \texttt{multiplechoice}). 
Ilustramos como parametrizar o template: seja $a=||intA||$ e $b=||intB||$,
quanto é $a+b$?

\begin{enumerate}
\item \grade{1} $||sumAB||$
\item $||dis1||$\feedback{Calculou a subtração $a - b$}
\item $||dis2||$
\item $||dis3||$
\item $||dis4||$
\end{enumerate}
\end{multiplechoice}

\end{document}'''.decode('utf8')

#===============================================================================
# main.lyx
#===============================================================================
MAIN_LYX = r'''#LyX 2.0 created this file. For more info see http://www.lyx.org/
\lyxformat 413
\begin_document
\begin_header
\textclass article
\begin_preamble
\usepackage{pytutor}
\usepackage{babel}
\end_preamble
\use_default_options false
\maintain_unincluded_children false
\language brazilian
\language_package default
\inputencoding utf8
\fontencoding T1
\font_roman default
\font_sans default
\font_typewriter default
\font_default_family default
\use_non_tex_fonts false
\font_sc false
\font_osf false
\font_sf_scale 100
\font_tt_scale 100

\graphics default
\default_output_format default
\output_sync 0
\bibtex_command default
\index_command default
\paperfontsize default
\spacing single
\use_hyperref false
\papersize default
\use_geometry false
\use_amsmath 1
\use_esint 1
\use_mhchem 0
\use_mathdots 0
\cite_engine basic
\use_bibtopic false
\use_indices false
\paperorientation portrait
\suppress_date false
\use_refstyle 0
\index Índice
\shortcut idx
\color #008000
\end_index
\secnumdepth 3
\tocdepth 3
\paragraph_separation indent
\paragraph_indentation default
\quotes_language english
\papercolumns 1
\papersides 1
\paperpagestyle default
\tracking_changes false
\output_changes false
\html_math_output 0
\html_css_as_file 0
\html_be_strict false
\end_header

\begin_body

\begin_layout Title
%(title)s
\end_layout

\begin_layout Date
12/12/2012
\end_layout

\begin_layout Author
%(author)s
\end_layout

\begin_layout Standard
\begin_inset ERT
status open

\begin_layout Plain Layout


\backslash
begin{introtext}
\end_layout

\end_inset

 Esta é uma questão exemplo.
 Normalmente as questões iniciam com um texto introdutório que deve ser
 marcado em latex com o ambiente 
\family typewriter
intro
\family default
.
 Lembre-se que no 
\begin_inset ERT
status open

\begin_layout Plain Layout

LyX
\end_layout

\end_inset

 é possível adicionar comandos LaTeX
\begin_inset space \space{}
\end_inset

arbitrários utilizando as caixas de código TeX
\begin_inset space \space{}
\end_inset

(ctrl+L).
 As marcações definidas pelo sistema tutor estão definidas no pacote 
\family typewriter
pytutor
\family default
 e portanto o documento deve incluir uma cláusula 
\family typewriter

\backslash
usepackage{pytutor}
\family default
 no preâmbulo.
 Este arquivo de exemplo já contêm a estrutura básica esperada para uma
 questão e compila normalmente se o sistema 
\family typewriter
pytutor
\family default
 estiver corretamente instalado.
 
\begin_inset ERT
status open

\begin_layout Plain Layout


\backslash
end{introtext}
\end_layout

\end_inset


\end_layout

\begin_layout Standard
\begin_inset ERT
status collapsed

\begin_layout Plain Layout


\backslash
begin{multiplechoice}
\end_layout

\end_inset

 Em uma questão normal, o texto acima seria relevante para resolução da
 mesma.
 Nesta questão de exemplo, ele não é.
 O ambiente 
\family typewriter
intro
\family default
 sequer é necessário já que o comando principal da questão pode ser incluído
 diretamente junto com o ambiente que define o tipo de quetão a ser abordada
 (e.g.
 
\family typewriter
multiplechoice
\family default
).
 Ilustramos como parametrizar o template: seja 
\begin_inset Formula $a=||intA||$
\end_inset

 e 
\begin_inset Formula $b=||intB||$
\end_inset

, quanto é 
\begin_inset Formula $a+b$
\end_inset

?
\end_layout

\begin_layout Enumerate
\begin_inset ERT
status collapsed

\begin_layout Plain Layout


\backslash
grade
\end_layout

\end_inset


\begin_inset ERT
status collapsed

\begin_layout Plain Layout

{
\end_layout

\end_inset

1
\begin_inset ERT
status collapsed

\begin_layout Plain Layout

}
\end_layout

\end_inset

 
\begin_inset Formula $||sumAB||$
\end_inset

 
\end_layout

\begin_layout Enumerate
\begin_inset Formula $||dis1||$
\end_inset


\begin_inset ERT
status collapsed

\begin_layout Plain Layout


\backslash
feedback
\end_layout

\end_inset


\begin_inset ERT
status collapsed

\begin_layout Plain Layout

{
\end_layout

\end_inset

Calculou a subtração 
\begin_inset Formula $a-b$
\end_inset


\begin_inset ERT
status collapsed

\begin_layout Plain Layout

}
\end_layout

\end_inset

 
\end_layout

\begin_layout Enumerate
\begin_inset Formula $||dis2||$
\end_inset

 
\end_layout

\begin_layout Enumerate
\begin_inset Formula $||dis3||$
\end_inset

 
\end_layout

\begin_layout Enumerate
\begin_inset Formula $||dis4||$
\end_inset

 
\end_layout

\begin_layout Standard
\begin_inset ERT
status collapsed

\begin_layout Plain Layout


\backslash
end{multiplechoice}
\end_layout

\end_inset


\end_layout

\end_body
\end_document'''.decode('utf8')

#===============================================================================
# src/main.*
#===============================================================================
MAIN = {'tex': MAIN_TEX, 'lyx': MAIN_LYX}
