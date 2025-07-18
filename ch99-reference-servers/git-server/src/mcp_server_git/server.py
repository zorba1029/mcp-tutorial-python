import logging
from pathlib import Path
from typing import Sequence, Optional
from mcp.server import Server
from mcp.server.session import ServerSession
from mcp.server.stdio import stdio_server
from mcp.types import (
    ClientCapabilities,
    TextContent,
    Tool,
    ListRootsResult,
    RootsCapability,
)
from enum import Enum
import git 
from pydantic import BaseModel, Field

# Default number of context lines to show in diff output
DEFAULT_CONTEXT_LINES = 3

#=============================================================
class GitStatus(BaseModel):
    repo_path: str

class GitDiffUnstaged(BaseModel):
    repo_path: str
    context_lines: int = DEFAULT_CONTEXT_LINES
    
class GitDiffStaged(BaseModel):
    repo_path: str
    context_lines: int = DEFAULT_CONTEXT_LINES
    
class GitDiff(BaseModel):
    repo_path: str
    target: str
    context_lines: int = DEFAULT_CONTEXT_LINES
    
class GitCommit(BaseModel):
    repo_path: str
    message: str
    
class GitAdd(BaseModel):
    repo_path: str
    file_path: str
    
class GitReset(BaseModel):
    repo_path: str

class GitLog(BaseModel):
    repo_path: str
    max_count: int = 10

class GitCreateBranch(BaseModel):
    repo_path: str
    branch_name: str
    base_branch: str | None = None
    
class GitDeleteBranch(BaseModel):
    repo_path: str
    branch_name: str
class GitCheckout(BaseModel):
    repo_path: str
    branch_name: str
    
class GitShow(BaseModel):
    repo_path: str
    revision: str
    
class GitInit(BaseModel):
    repo_path: str
    
class GitBranch(BaseModel):
    repo_path: str = Field(
        ..., 
        description="Path to the git repository",
    )
    branch_type: str = Field(
        ..., 
        description="Whether to list local branched ('local'), remote branches ('remote') or all branches ('all')",
    )
    contains: Optional[str] = Field(
        None,
        description="The commit sha that branch should contain. Do not pass anything to this param if no commit sha is specified",
    )
    not_contains: Optional[str] = Field(
        None,
        description="The commit sha that branch should NOT contain. Do not pass anything to this param if no commit sha is specified",
    )

class GitTools(str, Enum):
    STATUS = "git_status"
    DIFF_UNSTAGED = "git_diff_unstaged"
    DIFF_STAGED = "git_diff_staged"
    DIFF = "git_diff"
    COMMIT = "git_commit"
    ADD = "git_add"
    RESET = "git_reset"
    LOG = "git_log"
    CREATE_BRANCH = "git_create_branch"
    CHECKOUT = "git_checkout"
    SHOW = "git_show"
    INIT = "git_init"
    BRANCH = "git_branch"

#================================================    
def git_status(repo: git.Repo) -> str:
    return repo.git.status()

def git_diff_unstaged(repo: git.Repo, context_lines: int = DEFAULT_CONTEXT_LINES) -> str:
    return repo.git.diff(f"--unified={context_lines}")

def git_diff_staged(repo: git.Repo, context_lines: int = DEFAULT_CONTEXT_LINES) -> str:
    return repo.git.diff("--cached", f"--unified={context_lines}")

def git_diff(repo: git.Repo, target: str, context_lines: int = DEFAULT_CONTEXT_LINES) -> str:
    return repo.git.diff(target, f"--unified={context_lines}")

def git_commit(repo: git.Repo, message: str) -> str:
    commit = repo.index.commit(message)
    return f"Changes committed successfully with hash {commit.hexsha}"

def git_add(repo: git.Repo, files: list[str]) -> str:
    repo.git.add(files)
    return f"Files staged successfully."

def git_reset(repo: git.Repo) -> str:
    repo.git.reset()
    return "All staged changes reset."

def git_log(repo: git.Repo, max_count: int = 10) -> str:
    commits = list(repo.iter_commits(max_count=max_count))
    log = []
    for commit in commits:
        log.append(
            f"Commit: {commit.hexsha!r}\n"
            f"Author: {commit.author!r}\n"
            f"Date: {commit.authored_datetime}\n"
            f"Message: {commit.message!r}\n"
        )
    return "".join(log)

def git_create_branch(repo: git.Repo, branch_name: str, base_branch: str | None = None) -> str:
    if base_branch:
        base = repo.references[base_branch]
    else:
        base = repo.active_branch

    repo.create_head(branch_name)
    return f"Created branch '{branch_name}' from '{base.name}."

def git_checkout(repo: git.Repo, branch_name: str) -> str:
    repo.git.branch(branch_name)
    return f"Switched to Branch '{branch_name}'."

def git_init(repo_path: str) -> str:
    try:
        repo = git.Repo.init(path=repo_path, mkdir=True)
        return f"Initialized empty Git repository in '{repo.git_dir}'."
    except Exception as e:
        return f"Failed to initialize repository: {e}"
    
def git_show(repo: git.Repo, revision: str) -> str:
    try:
        commit = repo.commit(revision)
        output = [
            f"Commit: {commit.hexsha!r}\n",
            f"Author: {commit.author!r}\n",
            f"Date: {commit.authored_datetime}\n",
            f"Message: {commit.message!r}\n",
        ]
        if commit.parents:
            parent = commit.parents[0]
            diff  = parent.diff(commit, create_patch=True)
        else:
            diff = commit.diff(git.NULL_TREE, create_patch=True)
        
        for d in diff:
            output.append(f"\n-- {d.a_path}\n++ {d.b_path}\n")
            output.append(d.diff.decode('utf-8'))
        return "".join(output)
    except Exception as e:
        return f"Failed to show commit: {e}"
    
def git_branch(repo: git.Repo, branch_type: str, contains: str | None = None, not_contains: str | None = None) -> str:
    match contains:
        case None:
            contains_sha = (None,)
        case _:
            contains_sha = ("-contains", contains)
    
    match not_contains:
        case None:
            not_contains_sha = (None,)
        case _:
            not_contains_sha = ("--no-contains", not_contains)
        
    match branch_type:
        case "local":
            b_type = None
        case "remote":
            b_type = "-r"
        case "all":
            b_type = "-a"
        case _:
            return f"Invalid branch type: {branch_type}."
    
    # None value will be auto deleted by GitPython
    branch_info = repo.git.branch(b_type, *contains_sha, *not_contains_sha)
    
    return branch_info

#================================================
async def serve(repository: Path | None) -> None:
    logger = logging.getLogger(__name__)
    
    if repository is not None:
        try:
            git.Repo(repository)
            logger.info(f"Using repository at {repository}")
        except git.InvalidGitRepositoryError:
            logger.error(f"{repository} is not a vailed Git repository")
            return
        
    server = Server("mcp-git-server")
    
    #-------------------------------------------
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name=GitTools.STATUS,
                description="Shows the working tree statusy",
                inputSchema=GitStatus.model_json_schema(),
            ),
            Tool(
                name=GitTools.DIFF_UNSTAGED,
                description="Shows changes in the working directory that are not yet staged",
                inputSchema=GitDiffUnstaged.model_json_schema(),
            ),
            Tool(
                name=GitTools.DIFF_STAGED,
                description="Shows changes that are staged for commit",
                inputSchema=GitDiffStaged.model_json_schema(),
            ),
            Tool(
                name=GitTools.DIFF,
                description="Shows differences between branches or commits",
                inputSchema=GitDiff.model_json_schema(),
            ),
            Tool(
                name=GitTools.COMMIT,
                description="Records changes to the repository",
                inputSchema=GitCommit.model_json_schema(),
            ),
            Tool(
                name=GitTools.ADD,
                description="Adds file contents to the staging area",
                inputSchema=GitAdd.model_json_schema(),
            ),
            Tool(
                name=GitTools.RESET,
                description="Unstages all staged changes",
                inputSchema=GitReset.model_json_schema(),
            ),
            Tool(
                name=GitTools.LOG,
                description="Shows the commit logs",
                inputSchema=GitLog.model_json_schema(),
            ),
            Tool(
                name=GitTools.CREATE_BRANCH,
                description="Creates a new branch from an optional base branch",
                inputSchema=GitCreateBranch.model_json_schema(),
            ),
            Tool(
                name=GitTools.CHECKOUT,
                description="Switches branches",
                inputSchema=GitCheckout.model_json_schema(),
            ),
            Tool(
                name=GitTools.SHOW,
                description="Shows the contents of a commit",
                inputSchema=GitShow.model_json_schema(),
            ),
            Tool(
                name=GitTools.INIT,
                description="Initialize a new Git repository",
                inputSchema=GitInit.model_json_schema(),
            ),
            Tool(
                name=GitTools.BRANCH,
                description="List Git branches",
                inputSchema=GitBranch.model_json_schema(),
            )
        ]
        
    #-------------------------------------------
    async def list_repos() -> Sequence[str]:
        ##---------------------
        async def by_roots() -> Sequence[str]:
            if not isinstance(server.request_context.session, ServerSession):
                raise TypeError("server.request_context.session must be a ServerSession")
            
            if not server.request_context.session.check_client_capability(
                ClientCapabilities(roots=RootsCapability())
            ):
                return []

            roots_result: ListRootsResult  = await server.request_context.session.list_roots()
            logger.debug(f"Roots result: {roots_result}")
            repo_paths = []
            
            for root in roots_result.roots:
                path = root.uri.path
                try:
                    git.Repo(path)
                    repo_paths.append(str(path))
                except git.InvalidGitRepositoryError:
                    pass
            
            return repo_paths
        
        ##---------------------
        def by_commandline() -> Sequence[str]:
            return [str(repository)] if repository is not None else []
        
        cmd_repos = by_commandline()
        root_repos = await by_roots()
        return [*root_repos, *cmd_repos]

    #-------------------------------------------
    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        repo_path = Path(arguments["repo_path"])
        
        # handle git init separately since it doesn't require an existing repo
        if name == GitTools.INIT:
            result = git_init(str(repo_path))
            return [TextContent(type="text", text=result)]
        
        # For all other commands, we need an existing repo
        repo = git.Repo(repo_path)
        
        match name:
            case GitTools.STATUS:
                status = git_status(repo)
                return [TextContent(
                    type="text", 
                    text=f"Repository status:\n{status}"
                )]
            case GitTools.DIFF_UNSTAGED:
                diff = git_diff_unstaged(repo, arguments.get("context_lines", DEFAULT_CONTEXT_LINES))
                return [TextContent(
                    type="text", 
                    text=f"Unstaged changes:\n{diff}"
                )]
            case GitTools.DIFF_STAGED:
                diff = git_diff_staged(repo, arguments.get("context_lines", DEFAULT_CONTEXT_LINES))
                return [TextContent(
                    type="text", 
                    text=f"Staged changes:\n{diff}"
                )]
            case GitTools.DIFF:
                diff = git_diff(repo, arguments["target"], arguments.get("context_lines", DEFAULT_CONTEXT_LINES))
                return [TextContent(
                    type="text", 
                    text=f"Diff with {arguments['target']}:\n{diff}"
                )]
            case GitTools.COMMIT:
                result = git_commit(repo, arguments["message"])
                return [TextContent(
                    type="text", 
                    text=result
                )]
            case GitTools.ADD:
                result = git_add(repo, arguments["files"])
                return [TextContent(
                    type="text", 
                    text=result
                )]
            case GitTools.RESET:
                result = git_reset(repo)
                return [TextContent(
                    type="text", 
                    text=result
                )]
            case GitTools.LOG:
                log = git_log(repo, arguments.get("max_count", 10))
                return [TextContent(
                    type="text", 
                    text="Commit history:\n" + "".join(log)
                )]
            case GitTools.CREATE_BRANCH:
                result = git_create_branch(
                    repo, 
                    arguments["branch_name"], 
                    arguments.get("base_branch")
                )
                return [TextContent(
                    type="text", 
                    text=result
                )]
            case GitTools.CHECKOUT:
                result = git_checkout(repo, arguments["branch_name"])
                return [TextContent(
                    type="text", 
                    text=result
                )]
            case GitTools.SHOW:
                result = git_show(repo, arguments["revision"])
                return [TextContent(
                    type="text", 
                    text=result
                )]
            case GitTools.BRANCH:
                result = git_branch(
                    repo, 
                    arguments.get("branch_type", 'local'), 
                    arguments.get("contains", None), 
                    arguments.get("not_contains", None)
                )
                return [TextContent(
                    type="text", 
                    text=result
                )]
            case _:
                raise ValueError(f"Invalid tool name: {name}")
                
    #-------------------------------------------
    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)

#-- 실행 방법
# cd ./ch99-reference-servers/git-server
# npx @modelcontextprotocol/inspector uv run python -m mcp_server_git --repository ../..
