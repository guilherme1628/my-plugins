"""
Interactive Selector
Sistema de seleção navegável com suporte a teclas de seta.
"""

import sys
import tty
import termios
from typing import List, Dict, Any, Optional


class InteractiveSelector:
    """Seletor interativo navegável para listas."""
    
    def __init__(self):
        self.up_key = b'\x1b[A'
        self.down_key = b'\x1b[B'
        self.enter_key = b'\r'
        self.escape_key = b'\x1b'
        
    def _getch(self) -> bytes:
        """Captura uma tecla pressionada."""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.buffer.read(1)
            # Se for uma sequência de escape, ler caracteres adicionais
            if ch == b'\x1b':
                ch += sys.stdin.buffer.read(2)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
    
    def _clear_lines(self, count: int):
        """Limpa linhas específicas do terminal de forma simples."""
        if count <= 0:
            return
        try:
            # Método mais simples: mover para cima e limpar linha a linha
            for _ in range(count):
                sys.stdout.write('\033[1A\033[K')  # Move up one line and clear it
            sys.stdout.flush()
        except:
            # Fallback: apenas imprimir espaços em branco para "limpar"
            pass
    
    def _clear_screen_section(self, lines_to_clear: int):
        """Limpa seção específica sem mover o terminal todo."""
        # Move cursor para cima e limpa
        if lines_to_clear > 0:
            sys.stdout.write(f'\033[{lines_to_clear}A')  # Move up N lines
            for _ in range(lines_to_clear):
                sys.stdout.write('\033[K\n')  # Clear line and move to next
            sys.stdout.write(f'\033[{lines_to_clear}A')  # Move back up
            sys.stdout.flush()
    
    def _display_options(self, options: List[str], selected_index: int, title: str = ""):
        """Exibe as opções com destaque na seleção atual."""
        if title:
            sys.stdout.write(f"\n{title}\n")
            sys.stdout.write("Use ↑/↓ para navegar, Enter para selecionar, Esc para cancelar\n\n")
        
        for i, option in enumerate(options):
            if i == selected_index:
                sys.stdout.write(f"→ \033[92m{option}\033[0m\n")  # Verde com seta
            else:
                sys.stdout.write(f"  {option}\n")
        sys.stdout.flush()
    
    def select_from_list(self, options: List[str], title: str = "Selecione uma opção:") -> Optional[int]:
        """
        Apresenta uma lista navegável para seleção.
        
        Args:
            options: Lista de opções para exibir
            title: Título da seleção
            
        Returns:
            Índice da opção selecionada ou None se cancelado
        """
        if not options:
            return None
            
        selected_index = 0
        
        # Método alternativo: re-renderizar tudo sempre
        while True:
            try:
                # Limpar tela
                sys.stdout.write('\033[2J\033[H')  # Clear screen and move to top
                
                # Exibir título
                if title:
                    sys.stdout.write(f"{title}\n")
                    sys.stdout.write("Use ↑/↓ para navegar, Enter para selecionar, Esc para cancelar\n\n")
                
                # Exibir opções
                for i, option in enumerate(options):
                    if i == selected_index:
                        sys.stdout.write(f"→ \033[92m{option}\033[0m\n")  # Verde com seta
                    else:
                        sys.stdout.write(f"  {option}\n")
                
                sys.stdout.flush()
                
                key = self._getch()
                
                if key == self.up_key:
                    selected_index = (selected_index - 1) % len(options)
                elif key == self.down_key:
                    selected_index = (selected_index + 1) % len(options)
                elif key == self.enter_key:
                    return selected_index
                elif key == self.escape_key or key == b'\x03':  # Esc ou Ctrl+C
                    return None
                
            except KeyboardInterrupt:
                return None
            except Exception as e:
                # Se houver erro com terminal, voltar para seleção numérica simples
                print(f"\n❌ Erro na interface: {e}")
                print("Voltando para seleção numérica...")
                return self._fallback_selection(options, title)
    
    def _fallback_selection(self, options: List[str], title: str = "") -> Optional[int]:
        """Seleção numérica simples como fallback."""
        print(f"\n{title}")
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        
        while True:
            try:
                choice = input(f"\nEscolha (1-{len(options)}) ou Enter para cancelar: ").strip()
                if not choice:
                    return None
                choice_num = int(choice)
                if 1 <= choice_num <= len(options):
                    return choice_num - 1
                else:
                    print("❌ Opção inválida. Tente novamente.")
            except ValueError:
                print("❌ Digite um número válido.")
            except KeyboardInterrupt:
                return None
    
    def select_template(self, templates: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Seletor específico para templates.
        
        Args:
            templates: Lista de templates do Google Drive
            
        Returns:
            Template selecionado ou None se cancelado
        """
        if not templates:
            return None
        
        # Preparar opções para exibição
        options = []
        for template in templates:
            name = template['name']
            modified = template['modified'][:10] if 'modified' in template else 'N/A'
            options.append(f"{name} (modificado: {modified})")
        
        # Usar seletor
        selected_index = self.select_from_list(
            options, 
            "📄 Selecione um template:"
        )
        
        if selected_index is not None:
            return templates[selected_index]
        return None
    
    def select_data_file(self, data_files: List[Any], data_collector) -> Optional[Any]:
        """
        Seletor específico para arquivos de dados coletados.
        
        Args:
            data_files: Lista de arquivos Path
            data_collector: Instância do DataCollector para carregar dados
            
        Returns:
            Arquivo selecionado ou None se cancelado
        """
        if not data_files:
            return None
        
        # Preparar opções para exibição
        options = []
        sorted_files = sorted(data_files, key=lambda x: x.stat().st_mtime, reverse=True)
        
        for file in sorted_files:
            try:
                result = data_collector.load_from_file(file)
                # Usar nome do arquivo (que já inclui template) sem extensão
                file_display = file.stem  # Remove .json
                date_str = result.collected_at[:19].replace("T", " ")
                fields_count = len(result.data)
                
                options.append(f"{file_display} - {fields_count} campos ({date_str})")
            except Exception:
                # Se houver erro ao carregar, mostrar só o nome do arquivo
                options.append(f"{file.name} (erro ao ler)")
        
        # Usar seletor
        selected_index = self.select_from_list(
            options, 
            "📊 Selecione dados coletados:"
        )
        
        if selected_index is not None:
            return sorted_files[selected_index]
        return None
    
    def select_multiple_fields(self, fields: List[str], title: str = "Selecione campos para o nome do arquivo:") -> List[str]:
        """
        Seletor múltiplo para campos de nomenclatura.
        
        Args:
            fields: Lista de nomes de campos disponíveis
            title: Título da seleção
            
        Returns:
            Lista de campos selecionados na ordem escolhida
        """
        if not fields:
            return []
        
        selected_fields = []
        available_fields = fields.copy()
        current_index = 0
        first_render = True
        
        # Mostrar cabeçalho inicial
        print(f"\n{title}")
        print("Use ↑/↓ para navegar, Espaço para selecionar, Enter para finalizar, Esc para cancelar\n")
        
        while available_fields:
            # Calcular quantas linhas vamos usar
            header_lines = 0 if first_render else 2  # Linhas de selecionados
            content_lines = len(available_fields) + 1  # Campos + FINALIZAR
            total_lines = header_lines + content_lines
            
            # Limpar apenas a área de conteúdo (não o cabeçalho)
            if not first_render:
                self._clear_screen_section(total_lines)
            
            # Mostrar campos já selecionados (compacto)
            if selected_fields:
                selected_display = []
                for field in selected_fields:
                    selected_display.append(f"[x] {field}")
                print(f"Selecionados: {' + '.join(selected_display)}")
                print()
            
            # Mostrar opções disponíveis
            for i, field in enumerate(available_fields):
                if i == current_index:
                    print(f"\033[92m[ ] {field}\033[0m")  # Linha verde completa
                else:
                    print(f"[ ] {field}")
            
            # Opção para finalizar
            finish_option = "[ FINALIZAR ]"
            if current_index == len(available_fields):
                print(f"\033[92m{finish_option}\033[0m")  # Verde completo
            else:
                print(f"{finish_option}")
            
            first_render = False
            
            try:
                key = self._getch()
                
                if key == self.up_key:
                    current_index = (current_index - 1) % (len(available_fields) + 1)
                elif key == self.down_key:
                    current_index = (current_index + 1) % (len(available_fields) + 1)
                elif key == b' ':  # Espaço para selecionar
                    if current_index < len(available_fields):
                        selected_field = available_fields.pop(current_index)
                        selected_fields.append(selected_field)
                        # Ajustar índice se necessário
                        if current_index >= len(available_fields) and available_fields:
                            current_index = len(available_fields) - 1
                        elif not available_fields:
                            current_index = 0  # Vai para FINALIZAR
                elif key == self.enter_key:
                    if current_index == len(available_fields):  # FINALIZAR selecionado
                        break
                    elif available_fields:  # Selecionar campo atual
                        selected_field = available_fields.pop(current_index)
                        selected_fields.append(selected_field)
                        if current_index >= len(available_fields) and available_fields:
                            current_index = len(available_fields) - 1
                        elif not available_fields:
                            current_index = 0
                elif key == self.escape_key or key == b'\x03':  # Esc ou Ctrl+C
                    return []
                    
            except KeyboardInterrupt:
                return []
        
        return selected_fields