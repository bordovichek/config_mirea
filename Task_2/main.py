import os
import configparser
import subprocess
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
import matplotlib.pyplot as plt


def read_config(config_path):
    config = configparser.ConfigParser()
    config.read(config_path)
    visualizer_path = config.get('DATA', 'visualizer_path')
    repo_path = config.get('DATA', 'repo_path')
    commit_date = config.get('DATA', 'commit_date')
    return visualizer_path, repo_path, commit_date


def clone_repository(repo_url, target_dir):
    try:
        subprocess.run(['git', 'clone', repo_url, target_dir], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при клонировании репозитория: {e}")
        exit()


def get_commits(repo_dir, commit_date):
    os.chdir(repo_dir)
    try:
        commits = subprocess.check_output(
            ['git', 'log', '--after={}'.format(commit_date), '--pretty=format:%H,%cd,%an', '--date=iso'],
            text=True
        ).strip().split('\n')
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при получении коммитов: {e}")
        return []
    commit_info = []
    for commit in commits:
        if not commit:
            return False
        commit_hash, commit_time, author = commit.split(',')
        files = subprocess.check_output(['git', 'show', '--name-only', '--pretty=format:', commit_hash],
                                        text=True).strip().split('\n')
        commit_info.append((commit_hash, commit_time, author, files))
    return commit_info


def get_commit_branch(commit_hash):
    try:
        branch = subprocess.check_output(
            ['git', 'branch', '--contains', commit_hash],
            text=True
        ).strip().split('\n')
        branch_names = [b.strip('* ') for b in branch]
        return branch_names
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при определении ветки для коммита {commit_hash}: {e}")
        return []


def build_branch_file_graph(commits):
    G = nx.DiGraph()
    branch_nodes = {}

    for commit_hash, commit_time, author, files in commits:
        branches = get_commit_branch(commit_hash)
        for branch in branches:
            if branch not in branch_nodes:
                branch_nodes[branch] = f"branch_{branch}"
                G.add_node(branch_nodes[branch], label=f"Ветка: {branch}")

            commit_node = f"commit_{commit_hash}"
            label = f"{commit_time}\n{author}"
            G.add_node(commit_node, label=label)
            G.add_edge(branch_nodes[branch], commit_node)

            for file in files:
                file_node = f"file_{file}"
                if file_node not in G:
                    G.add_node(file_node, label=f"File: {file}")
                G.add_edge(commit_node, file_node)
    return G


def generate_mermaid_graph(G):
    lines = ["graph TD"]
    for node in G.nodes:
        label = G.nodes[node].get('label', 'No label available').replace('\n', '<br>')
        lines.append(f"{node}[\"{label}\"]")
    for edge in G.edges:
        lines.append(f"{edge[0]} --> {edge[1]}")
    return "\n".join(lines)


def visualize_graph(G):
    # Определяем уровень каждого узла
    for node in G.nodes:
        if node.startswith("date_"):  # Узел даты
            G.nodes[node]['subset'] = 0
        elif node.startswith("branch_"):  # Узел ветки
            G.nodes[node]['subset'] = 1
        elif node.startswith("commit_"):  # Узел коммита
            G.nodes[node]['subset'] = 2
        elif node.startswith("file_"):  # Узел файла
            G.nodes[node]['subset'] = 3

    pos = nx.multipartite_layout(G, subset_key="subset")  # Расположение по уровням

    # Увеличиваем расстояние между узлами, уменьшаем длину рёбер
    for key in pos:
        pos[key][0] *= 1.5  # Увеличиваем расстояние по горизонтали
        pos[key][1] *= 1.5  # Увеличиваем расстояние по вертикали

    # Рисуем граф с прозрачными рёбрами
    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, with_labels=True, labels=nx.get_node_attributes(G, 'label'), node_size=2000,
            node_color='lightblue', font_size=8, arrowsize=10, edge_color='gray', width=1.5, alpha=0.8)
    plt.show()


def get_branches(repo_dir):
    os.chdir(repo_dir)
    try:
        branches = subprocess.check_output(['git', 'branch', '-r'], text=True).strip().split('\n')
        branches = [branch.strip().replace('origin/', '') for branch in branches]
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при получении веток: {e}")
        return []
    return branches


def main():
    config_path = 'config_2.ini'
    visualizer_path, repo_url, commit_date = read_config(config_path)
    repo_name = repo_url.split('/')[-1].replace('.git', '')
    clone_repository(repo_url, repo_name)

    commits = get_commits(repo_name, commit_date)
    if not commits:
        print("Нет коммитов после указанной даты.")
        return

    G = build_branch_file_graph(commits)
    mermaid_graph = generate_mermaid_graph(G)

    print(mermaid_graph)

    visualize_graph(G)


if __name__ == "__main__":
    main()
