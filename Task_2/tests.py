import unittest
from unittest.mock import patch, MagicMock
from main import *  # Импортируем все функции из основного файла


class TestGitVisualization(unittest.TestCase):

    @patch('configparser.ConfigParser.get')
    def test_read_config(self, mock_get):
        mock_get.return_value = 'mock_value'
        config_path = 'config.ini'
        visualizer_path, repo_path, commit_date = read_config(config_path)
        mock_get.assert_any_call('DATA', 'visualizer_path')
        mock_get.assert_any_call('DATA', 'repo_path')
        mock_get.assert_any_call('DATA', 'commit_date')
        self.assertEqual(visualizer_path, 'mock_value')
        self.assertEqual(repo_path, 'mock_value')
        self.assertEqual(commit_date, 'mock_value')

    @patch('subprocess.run')
    def test_clone_repository(self, mock_run):
        mock_run.return_value = None
        repo_url = 'https://mock_repo.git'
        target_dir = 'mock_dir'
        clone_repository(repo_url, target_dir)
        mock_run.assert_called_once_with(['git', 'clone', repo_url, target_dir], check=True)

    @patch('subprocess.check_output')
    @patch('os.chdir')
    def test_get_commits(self, mock_chdir, mock_check_output):
        mock_check_output.return_value = 'mock_commit_hash,2024-01-01,Author\nmock_commit_hash_2,2024-01-02,Author2'
        repo_dir = 'mock_repo'
        commit_date = '2024-01-01'
        commits = get_commits(repo_dir, commit_date)
        mock_chdir.assert_called_once_with(repo_dir)
        mock_check_output.assert_any_call(
            ['git', 'log', '--after=2024-01-01', '--pretty=format:%H,%cd,%an', '--date=iso'], text=True)
        self.assertEqual(len(commits), 2)
        self.assertEqual(commits[0][0], 'mock_commit_hash')

    @patch('subprocess.check_output')
    def test_get_commit_branch(self, mock_check_output):
        mock_check_output.return_value = '* main\n  dev'
        commit_hash = 'mock_commit_hash'
        branches = get_commit_branch(commit_hash)
        self.assertIn('main', branches)
        self.assertIn('dev', branches)

    @patch('subprocess.check_output')
    def test_build_branch_file_graph(self, mock_check_output):
        mock_check_output.return_value = 'mock_parent_hash'
        commits = [
            ('mock_commit_hash', '2024-01-01', 'Author', ['file1', 'file2']),
            ('mock_commit_hash_2', '2024-01-02', 'Author2', ['file3'])]
        # Подготавливаем mock для веток
        with patch('main.get_commit_branch', return_value=['main', 'dev']):
            G = build_branch_file_graph(commits)
        self.assertEqual(len(G.nodes), 5)  # 2 коммита + 3 файла
        self.assertTrue(G.has_node('branch_main'))
        self.assertTrue(G.has_node('branch_dev'))
        self.assertTrue(G.has_edge('branch_main', 'commit_mock_commit_hash'))
        self.assertTrue(G.has_edge('commit_mock_commit_hash', 'file_file1'))

    @patch('subprocess.check_output')
    def test_get_branches(self, mock_check_output):
        mock_check_output.return_value = 'origin/main\norigin/dev\norigin/feature'
        repo_dir = 'mock_repo'
        branches = get_branches(repo_dir)
        self.assertEqual(len(branches), 3)
        self.assertIn('main', branches)
        self.assertIn('dev', branches)

    def test_generate_mermaid_graph(self):
        G = nx.DiGraph()
        G.add_node('A', label='Commit A')
        G.add_node('B', label='Commit B')
        G.add_edge('A', 'B')
        mermaid_graph = generate_mermaid_graph(G)
        self.assertIn("A[\"Commit A\"]", mermaid_graph)
        self.assertIn("A --> B", mermaid_graph)

    @patch('matplotlib.pyplot.show')
    def test_visualize_graph(self, mock_show):
        G = nx.DiGraph()
        G.add_node('A', label='Commit A')
        G.add_node('B', label='Commit B')
        G.add_edge('A', 'B')
        visualize_graph(G)
        mock_show.assert_called_once()


if __name__ == '__main__':
    unittest.main()
