// app/layout.tsx

// Este é o Root Layout principal para a aplicação Next.js 13+.

// Ele define a estrutura HTML básica, incluindo o cabeçalho, corpo e o layout do dashboard.

'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation'; // Importe usePathname para destacar o item de menu ativo

// Importe os estilos globais do Tailwind CSS.

// Certifique-se de que o arquivo globals.css (gerado pelo Tailwind) está importado aqui.

// NÃO inclua import "./dashboard.css"; ou qualquer outro CSS custom aqui.

import './globals.css'; // Este é o arquivo onde o Tailwind CSS é injetado.

// Componente de Layout do Dashboard

// Este componente encapsula toda a aplicação, fornecendo a estrutura do dashboard.

export default function RootLayout({

  children, // `children` representa o conteúdo da página atual

}: {

  children: React.ReactNode;

}) {

  // Estado para controlar se a sidebar está aberta ou fechada

  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  // Hook para obter o caminho atual da URL, usado para destacar o item de menu ativo

  const pathname = usePathname();



  // Função para alternar o estado da sidebar

  const toggleSidebar = () => {

    setIsSidebarOpen(!isSidebarOpen);

  };



  return (

    <html lang="pt-BR">

      <body>

        {/* Container principal do dashboard: usa flexbox para layout lateral */}

        <div className="flex min-h-screen bg-gray-100">

          {/* Sidebar: Largura condicional baseada no estado isSidebarOpen */}

          <aside

            className={`

              ${isSidebarOpen ? 'w-64' : 'w-16'} 

              bg-blue-900 text-white 

              p-4 

              transition-all duration-300 ease-in-out 

              fixed md:relative 

              h-screen 

              overflow-y-auto 

              z-30 

              hidden md:flex md:flex-col

              shadow-lg

            `}

          >

            {/* Logo/Título da Sidebar */}

            <div className="flex items-center justify-between mb-8">

              <h1 className={`text-2xl font-bold ${!isSidebarOpen && 'hidden'}`}>

                MedQuest

              </h1>

              {/* Botão para alternar a sidebar (visível apenas em telas maiores) */}

              <button

                onClick={toggleSidebar}

                className="p-2 rounded-full hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 md:hidden"

              >

                {isSidebarOpen ? (

                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>

                ) : (

                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>

                )}

              </button>

            </div>



            {/* Navegação da Sidebar */}

            <nav className="flex-1">

              <ul>

                {/* Item de menu: Home */}

                <li>

                  <Link href="/">

                    <div

                      className={`

                        flex items-center p-2 rounded-md text-sm font-medium 

                        ${pathname === '/' ? 'bg-blue-700' : 'hover:bg-blue-800'}

                        ${!isSidebarOpen && 'justify-center'}

                      `}

                    >

                      <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path></svg>

                      <span className={`${!isSidebarOpen && 'hidden'}`}>Dashboard</span>

                    </div>

                  </Link>

                </li>

                {/* Item de menu: Explicar Conceito */}

                <li className="mt-2">

                  <Link href="/explicar">

                    <div

                      className={`

                        flex items-center p-2 rounded-md text-sm font-medium 

                        ${pathname === '/explicar' ? 'bg-blue-700' : 'hover:bg-blue-800'}

                        ${!isSidebarOpen && 'justify-center'}

                      `}

                    >

                      <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6.253v13m0-13C10.832 5.477 9.205 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.523 5.795 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.795 5 16.5 5c1.705 0 3.332.477 4.5 1.253v13C19.832 18.523 18.205 18 16.5 18c-1.705 0-3.332.477-4.5 1.253"></path></svg>

                      <span className={`${!isSidebarOpen && 'hidden'}`}>Explicar</span>

                    </div>

                  </Link>

                </li>

                {/* Adicione mais itens de menu aqui, seguindo o padrão */}

                {/* Exemplo: Análise Crítica */}

                <li className="mt-2">

                  <Link href="/critica">

                    <div

                      className={`

                        flex items-center p-2 rounded-md text-sm font-medium 

                        ${pathname === '/critica' ? 'bg-blue-700' : 'hover:bg-blue-800'}

                        ${!isSidebarOpen && 'justify-center'}

                      `}

                    >

                      <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>

                      <span className={`${!isSidebarOpen && 'hidden'}`}>Crítica</span>

                    </div>

                  </Link>

                </li>

                {/* Exemplo: Upload PDF */}

                <li className="mt-2">

                  <Link href="/upload-pdf">

                    <div

                      className={`

                        flex items-center p-2 rounded-md text-sm font-medium 

                        ${pathname === '/upload-pdf' ? 'bg-blue-700' : 'hover:bg-blue-800'}

                        ${!isSidebarOpen && 'justify-center'}

                      `}

                    >

                      <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 0115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path></svg>

                      <span className={`${!isSidebarOpen && 'hidden'}`}>Upload PDF</span>

                    </div>

                  </Link>

                </li>

              </ul>

            </nav>

          </aside>



          {/* Conteúdo principal: ocupa o restante do espaço */}

          <div

            className={`

              flex-1 

              ${isSidebarOpen ? 'md:ml-64' : 'md:ml-16'} 

              transition-all duration-300 ease-in-out

              flex flex-col

            `}

          >

            {/* Header fixo no topo */}

            <header className="bg-blue-900 text-white p-4 shadow-md sticky top-0 z-20 flex items-center justify-between">

              {/* Botão para alternar a sidebar (visível em telas pequenas) */}

              <button

                onClick={toggleSidebar}

                className="p-2 rounded-full hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 md:hidden"

              >

                {isSidebarOpen ? (

                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>

                ) : (

                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>

                )}

              </button>

              <h2 className="text-xl font-semibold">MedQuest Research Dashboard</h2>

              {/* Placeholder para informações do usuário ou logout */}

              <div className="flex items-center">

                <span className="mr-2 text-sm">Dr. Edesio Martins</span>

                <button className="p-2 rounded-full hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500">

                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path></svg>

                </button>

              </div>

            </header>



            {/* Conteúdo principal da página (children) */}

            <main className="flex-1 p-6 bg-gray-100">

              {children}

            </main>

          </div>

        </div>

      </body>

    </html>

  );

}
