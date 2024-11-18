import os
import configparser
import subprocess
import networkx as nx
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
        commit_hash, commit_time, author = commit.split(',')
        files = subprocess.check_output(['git', 'show', '--name-only', '--pretty=format:', commit_hash],
                                        text=True).strip().split('\n')
        commit_info.append((commit_hash, commit_time, author, files))
    return commit_info


def build_dependency_graph(commits):
    G = nx.DiGraph()
    for commit_hash, commit_time, author, files in commits:
        label = f"{commit_time}\n{author}\nFiles:\n" + "\n".join(files)
        G.add_node(commit_hash, label=label)
        try:
            parents = subprocess.check_output(['git', 'rev-parse', '--parents', commit_hash], text=True)
            for parent_hash in parents.strip().split():
                if parent_hash != commit_hash:
                    G.add_edge(parent_hash, commit_hash)
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при получении родителей коммита {commit_hash}: {e}")
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
    pos = nx.spring_layout(G)
    labels = nx.get_node_attributes(G, 'label')
    nx.draw(G, pos, with_labels=True, labels=labels, node_size=2000, node_color='lightblue', font_size=8)
    plt.show()


def main():
    config_path = 'config_2.ini'
    visualizer_path, repo_url, commit_date = read_config(config_path)
    repo_name = repo_url.split('/')[-1].replace('.git', '')
    clone_repository(repo_url, repo_name)

    commits = get_commits(repo_name, commit_date)
    if not commits:
        print("Нет коммитов после указанной даты.")
        return

    G = build_dependency_graph(commits)
    mermaid_graph = generate_mermaid_graph(G)

    print(mermaid_graph)

    visualize_graph(G)


if __name__ == "__main__":
    main()
