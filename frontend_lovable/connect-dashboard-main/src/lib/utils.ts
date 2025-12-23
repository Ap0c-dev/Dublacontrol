import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Normaliza texto: primeira letra de cada palavra maiúscula, resto minúscula.
 * Similar à função normalizar_texto do backend.
 * Preserva espaços durante a digitação.
 */
export function capitalizarNome(texto: string): string {
  if (!texto) {
    return texto;
  }
  
  // Dividir o texto em palavras e espaços, preservando ambos
  // Usar regex para separar palavras de espaços
  const partes = texto.split(/(\s+)/);
  
  const resultado = partes.map(parte => {
    // Se for apenas espaços, manter como está
    if (/^\s+$/.test(parte)) {
      return parte;
    }
    // Se for uma palavra (mesmo que parcial), capitalizar
    if (parte.length > 0) {
      return parte[0].toUpperCase() + (parte.length > 1 ? parte.slice(1).toLowerCase() : '');
    }
    return parte;
  });
  
  return resultado.join('');
}

/**
 * Gera um username baseado no nome + "voxen"
 * Formato: primeironome_voxen
 * Remove acentos e caracteres especiais
 */
export function gerarUsernameVoxen(nome: string): string {
  if (!nome || nome.trim() === '') {
    return '';
  }
  
  // Normalizar: remover acentos
  const nomeNormalizado = nome
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase();
  
  // Remover caracteres especiais, manter apenas letras, números e espaços
  const nomeLimpo = nomeNormalizado.replace(/[^a-z0-9\s]/g, '');
  
  // Pegar primeiro nome
  const primeiroNome = nomeLimpo.split(/\s+/)[0] || 'user';
  
  // Se o primeiro nome for muito curto, usar mais palavras
  if (primeiroNome.length < 3) {
    const palavras = nomeLimpo.split(/\s+/).slice(0, 2);
    const nomeCompleto = palavras.join('_').substring(0, 20);
    return nomeCompleto ? `${nomeCompleto}_voxen` : 'user_voxen';
  }
  
  return `${primeiroNome}_voxen`;
}
