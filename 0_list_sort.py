from __future__ import annotations
from pathlib import Path


def load_numbers(path: Path) -> list[str]:
    if not path.exists():
        print(f"Arquivo não encontrado: {path}. Nenhum conteúdo foi carregado.")
        return []

    with path.open("r", encoding="utf-8") as file:
        lines = [line.rstrip("\n") for line in file]

    return [line for line in lines if line.strip()]


def sort_numbers(lines: list[str]) -> list[str]:
    try:
        return sorted(lines, key=lambda value: value.strip())
    except ValueError:
        return sorted(lines, key=lambda value: value.strip())


def save_numbers(path: Path, lines: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as file:
        if lines:
            file.write("\n".join(lines) + "\n")


def list_txt_files(directory: Path) -> list[Path]:
    """Lista todos os arquivos .txt do diretório."""
    return sorted(directory.glob("*.txt"))


def select_file(files: list[Path]) -> Path:
    """Permite o usuário selecionar um arquivo da lista."""
    if not files:
        print("Nenhum arquivo .txt encontrado no diretório.")
        return None

    print("\n=== Arquivos .txt disponíveis ===")
    for idx, file in enumerate(files, 1):
        print(f"{idx}. {file.name}")

    while True:
        try:
            choice = input(f"\nSelecione o arquivo (1-{len(files)}): ").strip()
            index = int(choice) - 1
            if 0 <= index < len(files):
                return files[index]
            else:
                print(f"Escolha inválida. Digite um número entre 1 e {len(files)}.")
        except ValueError:
            print("Entrada inválida. Digite um número.")


def main() -> None:
    # Obtém o diretório do script
    current_dir = Path.cwd()

    # Lista arquivos .txt
    txt_files = list_txt_files(current_dir)

    # Usuário seleciona o arquivo
    selected_file = select_file(txt_files)
    if not selected_file:
        return

    print(f"\nOrdenando: {selected_file.name}")

    # Carrega, ordena e salva o arquivo
    lines = load_numbers(selected_file)
    sorted_lines = sort_numbers(lines)
    save_numbers(selected_file, sorted_lines)

    print(f"✓ Arquivo ordenado com sucesso: {selected_file}")


if __name__ == "__main__":
    main()
