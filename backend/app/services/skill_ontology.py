from enum import Enum
from typing import NamedTuple


class SkillCategory(str, Enum):
    PROGRAMMING_LANGUAGE = "Programming Language"
    FRONTEND_FRAMEWORK = "Frontend Framework"
    BACKEND_FRAMEWORK = "Backend Framework"
    CLOUD_DEVOPS = "Cloud & DevOps"
    DATABASE = "Database"
    DATA_SCIENCE_AI = "Data Science & AI"
    DESIGN_UIUX = "Design & UI/UX"
    TESTING_QA = "Testing & QA"
    METHODOLOGY = "Methodology & Architecture"
    DOMAIN_KNOWLEDGE = "Domain Knowledge"
    OTHER = "Other"


class RelationshipType(str, Enum):
    EXACT = "EXACT"
    ALIAS = "ALIAS"
    PARENT = "PARENT"
    CHILD = "CHILD"
    RELATED = "RELATED"
    ECOSYSTEM = "ECOSYSTEM"
    NONE = "NONE"


class SkillRelationship:
    def __init__(self, target_skill: str, relation_type: RelationshipType, description: str):
        self.target_skill = target_skill
        self.relation_type = relation_type
        self.description = description

    @property
    def rel_type(self) -> RelationshipType:
        return self.relation_type

    @property
    def similarity_weight(self) -> float:
        if self.relation_type in (RelationshipType.EXACT, RelationshipType.ALIAS):
            return 1.0
        elif self.relation_type == RelationshipType.ECOSYSTEM:
            return 0.6
        elif self.relation_type in (RelationshipType.PARENT, RelationshipType.CHILD):
            return 0.6
        elif self.relation_type == RelationshipType.RELATED:
            return 0.4
        return 0.0


class SkillDefinition:
    def __init__(
        self,
        skill_id: str,
        name: str,
        category: SkillCategory,
        aliases: list[str] | None = None,
        parent_skill: str | None = None,
        related_skills: list[str] | None = None,
        ecosystem: str | None = None,
        common_roles: list[str] | None = None,
        description: str = "",
    ):
        self.skill_id = skill_id
        self.name = name
        self.category = category
        self.aliases = [a.lower().strip() for a in (aliases or [])]
        self.parent_skill = parent_skill
        self.related_skills = related_skills or []
        self.ecosystem = ecosystem
        self.common_roles = common_roles or []
        self.description = description


class SkillOntology:
    """Enterprise Skill Knowledge Base and Ontology Graph for TalentLens AI.
    
    Provides:
    1. Canonical Skill Normalization (e.g. React.js -> React, TS -> TypeScript).
    2. Multi-Level Relationship Resolution (Exact, Alias, Parent, Child, Related, Ecosystem).
    3. Non-Equivalence Guarantee (React != Angular, Java != JavaScript, .NET != C#).
    4. Unknown Skill Handling (preserves and flags unknown skills for recruiter verification).
    """

    def __init__(self) -> None:
        self._skills: dict[str, SkillDefinition] = {}
        self._alias_map: dict[str, str] = {}  # lowercase alias/name -> canonical name
        self._load_knowledge_base()

    def _register_skill(self, skill: SkillDefinition) -> None:
        canonical = skill.name
        self._skills[canonical] = skill
        self._alias_map[canonical.lower()] = canonical
        for alias in skill.aliases:
            self._alias_map[alias.lower()] = canonical

    def _load_knowledge_base(self) -> None:
        # --- FRONTEND ECOSYSTEM ---
        self._register_skill(SkillDefinition(
            skill_id="fe_dev",
            name="Frontend Development",
            category=SkillCategory.METHODOLOGY,
            aliases=["frontend", "front-end", "front end", "client-side development", "web frontend"],
            common_roles=["Frontend Developer", "Full Stack Developer"],
            description="Developing user-facing web applications and interfaces.",
        ))

        self._register_skill(SkillDefinition(
            skill_id="responsive_design",
            name="Responsive Design",
            category=SkillCategory.METHODOLOGY,
            aliases=["responsive web design", "responsive web", "mobile responsive", "adaptive design"],
            parent_skill="Frontend Development",
            common_roles=["Frontend Developer", "UI/UX Designer"],
            description="Designing web applications that adapt to all screen sizes.",
        ))

        self._register_skill(SkillDefinition(
            skill_id="reusable_components",
            name="Reusable Components",
            category=SkillCategory.METHODOLOGY,
            aliases=["component-driven development", "component architecture", "modular ui"],
            parent_skill="Frontend Development",
            common_roles=["Frontend Developer"],
            description="Building modular, maintainable UI component libraries.",
        ))

        self._register_skill(SkillDefinition(
            skill_id="react",
            name="React",
            category=SkillCategory.FRONTEND_FRAMEWORK,
            aliases=["react.js", "reactjs", "react framework"],
            parent_skill="Frontend Development",
            related_skills=["JavaScript", "TypeScript", "Next.js", "Redux"],
            common_roles=["Frontend Developer", "Full Stack Developer"],
            description="A popular declarative JavaScript UI library.",
        ))

        self._register_skill(SkillDefinition(
            skill_id="nextjs",
            name="Next.js",
            category=SkillCategory.FRONTEND_FRAMEWORK,
            aliases=["next.js", "nextjs", "next js", "next"],
            parent_skill="React",
            related_skills=["React", "TypeScript", "Node.js"],
            ecosystem="React",
            common_roles=["Frontend Developer", "Full Stack Developer"],
            description="React server-side rendering and full-stack web framework.",
        ))

        self._register_skill(SkillDefinition(
            skill_id="angular",
            name="Angular",
            category=SkillCategory.FRONTEND_FRAMEWORK,
            aliases=["angular.js", "angularjs", "angular 2+", "angular framework"],
            parent_skill="Frontend Development",
            related_skills=["TypeScript", "RxJS", "JavaScript"],
            common_roles=["Frontend Developer", "Full Stack Developer"],
            description="Enterprise TypeScript-based web application framework by Google.",
        ))

        self._register_skill(SkillDefinition(
            skill_id="vue",
            name="Vue.js",
            category=SkillCategory.FRONTEND_FRAMEWORK,
            aliases=["vue", "vue.js", "vuejs", "vue 3", "nuxt", "nuxtjs"],
            parent_skill="Frontend Development",
            related_skills=["JavaScript", "TypeScript"],
            common_roles=["Frontend Developer", "Full Stack Developer"],
            description="Progressive JavaScript framework for building user interfaces.",
        ))

        self._register_skill(SkillDefinition(
            skill_id="typescript",
            name="TypeScript",
            category=SkillCategory.PROGRAMMING_LANGUAGE,
            aliases=["ts", "typescript lang"],
            related_skills=["JavaScript", "React", "Angular", "Node.js"],
            common_roles=["Frontend Developer", "Backend Developer", "Full Stack Developer"],
            description="Typed superset of JavaScript that compiles to plain JavaScript.",
        ))

        self._register_skill(SkillDefinition(
            skill_id="javascript",
            name="JavaScript",
            category=SkillCategory.PROGRAMMING_LANGUAGE,
            aliases=["js", "ecmascript", "es6", "vanilla js", "es2020"],
            related_skills=["TypeScript", "HTML5", "CSS3", "React", "Node.js"],
            common_roles=["Frontend Developer", "Full Stack Developer", "Backend Developer"],
            description="Standard programming language of the Web.",
        ))

        self._register_skill(SkillDefinition(
            skill_id="html5",
            name="HTML5",
            category=SkillCategory.PROGRAMMING_LANGUAGE,
            aliases=["html", "html5 markup", "hypertext markup language"],
            parent_skill="Frontend Development",
            related_skills=["CSS3", "JavaScript"],
            common_roles=["Frontend Developer", "Web Developer"],
            description="Standard markup language for web document structure.",
        ))

        self._register_skill(SkillDefinition(
            skill_id="css3",
            name="CSS3",
            category=SkillCategory.PROGRAMMING_LANGUAGE,
            aliases=["css", "cascading style sheets", "css3 styling", "sass", "scss", "tailwind", "tailwind css", "bootstrap"],
            parent_skill="Frontend Development",
            related_skills=["HTML5", "Responsive Design"],
            common_roles=["Frontend Developer", "UI/UX Designer"],
            description="Style sheet language used for describing web presentation.",
        ))

        # --- BACKEND & .NET ECOSYSTEM ---
        self._register_skill(SkillDefinition(
            skill_id="be_dev",
            name="Backend Development",
            category=SkillCategory.METHODOLOGY,
            aliases=["backend", "back-end", "back end", "server-side development"],
            common_roles=["Backend Developer", "Full Stack Developer"],
            description="Server-side application architecture and API development.",
        ))

        self._register_skill(SkillDefinition(
            skill_id="dotnet",
            name=".NET",
            category=SkillCategory.BACKEND_FRAMEWORK,
            aliases=[".net", "dotnet", ".net framework", ".net core", "microsoft .net"],
            parent_skill="Backend Development",
            related_skills=["C#", "ASP.NET Core", "Entity Framework", "SQL Server"],
            ecosystem=".NET",
            common_roles=["Backend Developer", "Full Stack Developer"],
            description="Microsoft open-source managed development platform.",
        ))

        self._register_skill(SkillDefinition(
            skill_id="csharp",
            name="C#",
            category=SkillCategory.PROGRAMMING_LANGUAGE,
            aliases=["c#", "csharp", "c sharp"],
            ecosystem=".NET",
            related_skills=[".NET", "ASP.NET Core", "LINQ", "Entity Framework"],
            common_roles=["Backend Developer", "Full Stack Developer"],
            description="Modern, object-oriented programming language for .NET ecosystem.",
        ))

        self._register_skill(SkillDefinition(
            skill_id="aspnet_core",
            name="ASP.NET Core",
            category=SkillCategory.BACKEND_FRAMEWORK,
            aliases=["asp.net core", "asp.net", "aspnetcore", "aspnet", "web api .net"],
            parent_skill=".NET",
            ecosystem=".NET",
            related_skills=["C#", ".NET", "REST API", "Entity Framework"],
            common_roles=["Backend Developer", "Full Stack Developer"],
            description="High-performance, cross-platform framework for building web apps on .NET.",
        ))

        # --- PYTHON & BACKEND ECOSYSTEM ---
        self._register_skill(SkillDefinition(
            skill_id="python",
            name="Python",
            category=SkillCategory.PROGRAMMING_LANGUAGE,
            aliases=["python", "py", "python3", "python 3"],
            related_skills=["FastAPI", "Django", "Flask", "Pandas", "PyTorch"],
            common_roles=["Backend Developer", "Data Scientist", "DevOps Engineer"],
            description="High-level, versatile programming language known for readability.",
        ))

        self._register_skill(SkillDefinition(
            skill_id="fastapi",
            name="FastAPI",
            category=SkillCategory.BACKEND_FRAMEWORK,
            aliases=["fastapi", "fast api"],
            parent_skill="Python",
            related_skills=["Python", "REST API", "Pydantic", "AsyncIO"],
            common_roles=["Backend Developer"],
            description="Modern, high-performance web framework for building APIs with Python.",
        ))

        self._register_skill(SkillDefinition(
            skill_id="django",
            name="Django",
            category=SkillCategory.BACKEND_FRAMEWORK,
            aliases=["django", "django rest framework", "drf"],
            parent_skill="Python",
            related_skills=["Python", "PostgreSQL", "REST API"],
            common_roles=["Backend Developer", "Full Stack Developer"],
            description="High-level Python web framework encouraging rapid development.",
        ))

        self._register_skill(SkillDefinition(
            skill_id="nodejs",
            name="Node.js",
            category=SkillCategory.BACKEND_FRAMEWORK,
            aliases=["node.js", "nodejs", "node"],
            related_skills=["JavaScript", "TypeScript", "Express.js", "NestJS"],
            common_roles=["Backend Developer", "Full Stack Developer"],
            description="Asynchronous event-driven JavaScript runtime environment.",
        ))

        self._register_skill(SkillDefinition(
            skill_id="java",
            name="Java",
            category=SkillCategory.PROGRAMMING_LANGUAGE,
            aliases=["java", "core java", "java 11", "java 17", "java 21"],
            related_skills=["Spring Boot", "Hibernate", "Microservices"],
            common_roles=["Backend Developer", "Enterprise Architect"],
            description="Class-based, object-oriented enterprise programming language.",
        ))

        self._register_skill(SkillDefinition(
            skill_id="spring_boot",
            name="Spring Boot",
            category=SkillCategory.BACKEND_FRAMEWORK,
            aliases=["spring boot", "spring", "spring framework"],
            parent_skill="Java",
            ecosystem="Java",
            related_skills=["Java", "Microservices", "REST API"],
            common_roles=["Backend Developer"],
            description="Opinionated Java framework for building stand-alone production applications.",
        ))

        self._register_skill(SkillDefinition(
            skill_id="rest_api",
            name="REST API",
            category=SkillCategory.METHODOLOGY,
            aliases=["rest api", "rest apis", "restful", "restful apis", "restful web services", "api development"],
            parent_skill="Backend Development",
            common_roles=["Backend Developer", "Full Stack Developer"],
            description="Architectural style for web services communication.",
        ))

        self._register_skill(SkillDefinition(
            skill_id="graphql",
            name="GraphQL",
            category=SkillCategory.METHODOLOGY,
            aliases=["graphql", "gql", "apollo graphql"],
            related_skills=["REST API", "Node.js", "TypeScript"],
            common_roles=["Backend Developer", "Full Stack Developer"],
            description="Query language for APIs and runtime for fulfilling queries with existing data.",
        ))

        # --- DATABASES ---
        self._register_skill(SkillDefinition(
            skill_id="sql",
            name="SQL",
            category=SkillCategory.DATABASE,
            aliases=["sql", "structured query language", "relational database", "rdbms"],
            related_skills=["PostgreSQL", "MySQL", "SQL Server"],
            common_roles=["Backend Developer", "Data Analyst", "Database Administrator"],
            description="Domain-specific language used in programming and managing relational databases.",
        ))

        self._register_skill(SkillDefinition(
            skill_id="postgresql",
            name="PostgreSQL",
            category=SkillCategory.DATABASE,
            aliases=["postgres", "postgresql", "psql"],
            parent_skill="SQL",
            related_skills=["SQL", "Database Optimization"],
            common_roles=["Backend Developer", "Database Administrator"],
            description="Powerful, open-source object-relational database system.",
        ))

        self._register_skill(SkillDefinition(
            skill_id="sql_server",
            name="SQL Server",
            category=SkillCategory.DATABASE,
            aliases=["mssql", "microsoft sql server", "sql server", "t-sql"],
            parent_skill="SQL",
            ecosystem=".NET",
            related_skills=["SQL", "C#", ".NET"],
            common_roles=["Backend Developer", "Database Administrator"],
            description="Microsoft relational database management system.",
        ))

        self._register_skill(SkillDefinition(
            skill_id="mongodb",
            name="MongoDB",
            category=SkillCategory.DATABASE,
            aliases=["mongo", "mongodb", "nosql mongodb"],
            related_skills=["NoSQL", "Node.js", "Express.js"],
            common_roles=["Backend Developer", "Full Stack Developer"],
            description="Document-based distributed NoSQL database.",
        ))

        self._register_skill(SkillDefinition(
            skill_id="go",
            name="Go",
            category=SkillCategory.PROGRAMMING_LANGUAGE,
            aliases=["golang", "go language", "go lang", "go programming"],
            related_skills=["Docker", "Kubernetes", "Microservices"],
            common_roles=["Backend Developer", "Cloud Engineer", "Systems Engineer"],
            description="Statically typed, compiled programming language designed at Google.",
        ))

        # --- CLOUD & DEVOPS ---
        self._register_skill(SkillDefinition(
            skill_id="cloud_computing",
            name="Cloud Computing",
            category=SkillCategory.CLOUD_DEVOPS,
            aliases=["cloud", "cloud platforms", "cloud architecture"],
            related_skills=["Microsoft Azure", "AWS", "Google Cloud Platform"],
            common_roles=["DevOps Engineer", "Cloud Engineer", "Cloud Architect"],
            description="On-demand delivery of compute, storage, and networking services over the Internet.",
        ))

        self._register_skill(SkillDefinition(
            skill_id="azure",
            name="Microsoft Azure",
            category=SkillCategory.CLOUD_DEVOPS,
            aliases=["azure", "microsoft azure", "azure cloud", "azure vms", "azure app services"],
            parent_skill="Cloud Computing",
            related_skills=["AWS", "Google Cloud Platform", "Cloud Computing"],
            common_roles=["Cloud Engineer", "DevOps Engineer", "Backend Developer"],
            description="Microsoft public cloud computing platform and services.",
        ))

        self._register_skill(SkillDefinition(
            skill_id="aws",
            name="AWS",
            category=SkillCategory.CLOUD_DEVOPS,
            aliases=["aws", "amazon web services", "aws cloud", "ec2", "s3", "lambda"],
            parent_skill="Cloud Computing",
            related_skills=["Microsoft Azure", "Google Cloud Platform", "Cloud Computing"],
            common_roles=["Cloud Engineer", "DevOps Engineer", "Backend Developer"],
            description="Amazon comprehensive and broadly adopted cloud platform.",
        ))

        self._register_skill(SkillDefinition(
            skill_id="gcp",
            name="Google Cloud Platform",
            category=SkillCategory.CLOUD_DEVOPS,
            aliases=["gcp", "google cloud", "google cloud platform"],
            parent_skill="Cloud Computing",
            related_skills=["AWS", "Microsoft Azure", "Cloud Computing"],
            common_roles=["Cloud Engineer", "Data Engineer"],
            description="Google suite of cloud computing services running on the same infrastructure as Google.",
        ))

        self._register_skill(SkillDefinition(
            skill_id="docker",
            name="Docker",
            category=SkillCategory.CLOUD_DEVOPS,
            aliases=["docker", "containerization", "containers", "docker containers", "dockerfile", "podman"],
            related_skills=["Kubernetes", "Container Orchestration"],
            common_roles=["DevOps Engineer", "Backend Developer", "Cloud Engineer"],
            description="Platform for building, sharing, and running containerized applications.",
        ))

        self._register_skill(SkillDefinition(
            skill_id="kubernetes",
            name="Kubernetes",
            category=SkillCategory.CLOUD_DEVOPS,
            aliases=["kubernetes", "k8s", "aks", "eks", "gke", "container orchestration"],
            related_skills=["Docker", "Cloud Computing", "Terraform"],
            common_roles=["DevOps Engineer", "Cloud Architect"],
            description="Open-source system for automating deployment, scaling, and management of containerized apps.",
        ))

        self._register_skill(SkillDefinition(
            skill_id="terraform",
            name="Terraform",
            category=SkillCategory.CLOUD_DEVOPS,
            aliases=["terraform", "iac", "infrastructure as code", "arm", "bicep"],
            related_skills=["AWS", "Microsoft Azure", "DevOps"],
            common_roles=["DevOps Engineer", "Cloud Architect"],
            description="Infrastructure as Code software tool that provides a consistent CLI workflow.",
        ))

        self._register_skill(SkillDefinition(
            skill_id="cicd",
            name="CI/CD",
            category=SkillCategory.CLOUD_DEVOPS,
            aliases=["ci/cd", "ci cd", "continuous integration", "continuous delivery", "github actions", "gitlab ci", "jenkins", "azure devops"],
            related_skills=["Docker", "Git", "DevOps"],
            common_roles=["DevOps Engineer", "Software Engineer"],
            description="Automated software delivery practice for building, testing, and deploying code.",
        ))

        self._register_skill(SkillDefinition(
            skill_id="git",
            name="Git",
            category=SkillCategory.METHODOLOGY,
            aliases=["git", "version control", "github", "gitlab", "bitbucket"],
            common_roles=["Software Engineer", "Frontend Developer", "Backend Developer"],
            description="Distributed version control system for tracking changes in source code.",
        ))

        # --- DESIGN & UI/UX ---
        self._register_skill(SkillDefinition(
            skill_id="ui_ux",
            name="UI/UX Design",
            category=SkillCategory.DESIGN_UIUX,
            aliases=["ui/ux", "ui design", "ux design", "product design", "user experience", "user interface", "wireframing", "prototyping"],
            related_skills=["Figma", "Sketch", "Adobe Creative Suite"],
            common_roles=["UI/UX Designer", "Product Designer"],
            description="Designing user-centered digital product interfaces and workflows.",
        ))

        self._register_skill(SkillDefinition(
            skill_id="figma",
            name="Figma",
            category=SkillCategory.DESIGN_UIUX,
            aliases=["figma", "figma design"],
            parent_skill="UI/UX Design",
            related_skills=["UI/UX Design", "Wireframing"],
            common_roles=["UI/UX Designer", "Frontend Developer"],
            description="Collaborative web-based design and prototyping tool.",
        ))

        self._register_skill(SkillDefinition(
            skill_id="sketch",
            name="Sketch",
            category=SkillCategory.DESIGN_UIUX,
            aliases=["sketch", "sketch app"],
            parent_skill="UI/UX Design",
            common_roles=["UI/UX Designer"],
            description="Digital design platform for macOS.",
        ))

        self._register_skill(SkillDefinition(
            skill_id="adobe_suite",
            name="Adobe Creative Suite",
            category=SkillCategory.DESIGN_UIUX,
            aliases=["adobe creative suite", "adobe suite", "photoshop", "illustrator", "adobe xd", "indesign"],
            parent_skill="UI/UX Design",
            common_roles=["Graphic Designer", "UI/UX Designer"],
            description="Industry-standard suite of graphic design, video editing, and web development applications.",
        ))

    def normalize_skill(self, raw_skill_name: str) -> tuple[str, bool]:
        """Normalize a skill name against the Knowledge Base.
        
        Returns:
            (canonical_name, is_known_in_ontology)
        """
        raw = raw_skill_name.strip()
        if not raw:
            return "", False
        
        lowered = raw.lower()
        if lowered in self._alias_map:
            return self._alias_map[lowered], True
        
        # Strip trailing parentheticals e.g. "React (v18)" -> "React"
        if "(" in raw:
            clean_base = raw.split("(", 1)[0].strip().lower()
            if clean_base in self._alias_map:
                return self._alias_map[clean_base], True

        # Return original capitalization if unknown, marked as unknown
        return raw, False

    def get_skill(self, canonical_name: str) -> SkillDefinition | None:
        return self._skills.get(canonical_name)

    def find_relationship(self, target_skill: str, candidate_skill: str) -> SkillRelationship:
        """Determines the exact ontology relationship between a target requirement and candidate skill.
        
        Returns a SkillRelationship object with relationship_type:
        - EXACT: Identical normalized technology or alias (e.g. React.js <-> React)
        - ECOSYSTEM: Part of the same technological ecosystem (e.g. .NET <-> C#, ASP.NET Core)
        - PARENT: Target is parent category of candidate (e.g. Frontend Dev <-> React)
        - CHILD: Candidate is parent category of target (e.g. React <-> Next.js)
        - RELATED: Relevant sibling/related skill (e.g. React <-> TypeScript, Angular <-> React as frontend framework)
        - NONE: No verified relationship.
        """
        target_norm, target_known = self.normalize_skill(target_skill)
        cand_norm, cand_known = self.normalize_skill(candidate_skill)

        if not target_norm or not cand_norm:
            return SkillRelationship(target_skill, RelationshipType.NONE, "Missing skill name")

        # 1. Exact canonical or alias match
        if target_norm.lower() == cand_norm.lower():
            return SkillRelationship(
                target_skill=target_norm,
                relation_type=RelationshipType.EXACT,
                description=f"Direct match with {cand_norm}",
            )

        # Non-equivalence safety checks:
        # React != Angular, Java != JavaScript, Python != Django, .NET != C# (ecosystem, not equal)
        if {target_norm.lower(), cand_norm.lower()} == {"react", "angular"}:
            return SkillRelationship(
                target_skill=target_norm,
                relation_type=RelationshipType.RELATED,
                description="Candidate has frontend framework experience through React, but Angular-specific experience is not demonstrated.",
            )

        if {target_norm.lower(), cand_norm.lower()} == {"react", "vue.js"}:
            return SkillRelationship(
                target_skill=target_norm,
                relation_type=RelationshipType.RELATED,
                description="Candidate has frontend framework experience through React/Vue, but the specific requested framework differs.",
            )

        if {target_norm.lower(), cand_norm.lower()} == {"angular", "vue.js"}:
            return SkillRelationship(
                target_skill=target_norm,
                relation_type=RelationshipType.RELATED,
                description="Candidate has frontend framework experience, but the target framework is not explicitly demonstrated.",
            )

        if {target_norm.lower(), cand_norm.lower()} == {"java", "javascript"}:
            return SkillRelationship(
                target_skill=target_norm,
                relation_type=RelationshipType.NONE,
                description="Java and JavaScript are entirely different programming languages.",
            )

        target_def = self.get_skill(target_norm)
        cand_def = self.get_skill(cand_norm)

        if target_def and cand_def:
            # 2. Ecosystem relationship (e.g. .NET <-> C# <-> ASP.NET Core)
            if target_def.ecosystem and target_def.ecosystem == cand_def.ecosystem:
                return SkillRelationship(
                    target_skill=target_norm,
                    relation_type=RelationshipType.ECOSYSTEM,
                    description=f"Belongs to the same {target_def.ecosystem} ecosystem.",
                )

            # 3. Parent / Child hierarchy (e.g. Frontend Development -> React)
            if cand_def.parent_skill == target_norm:
                return SkillRelationship(
                    target_skill=target_norm,
                    relation_type=RelationshipType.PARENT,
                    description=f"{cand_norm} satisfies parent requirement {target_norm}.",
                )

            if target_def.parent_skill == cand_norm:
                return SkillRelationship(
                    target_skill=target_norm,
                    relation_type=RelationshipType.CHILD,
                    description=f"Candidate has parent discipline {cand_norm}.",
                )

            # 4. Explicitly related skills
            if cand_norm in target_def.related_skills or target_norm in cand_def.related_skills:
                return SkillRelationship(
                    target_skill=target_norm,
                    relation_type=RelationshipType.RELATED,
                    description=f"Related technology to {target_norm}.",
                )

        return SkillRelationship(target_skill=target_norm, relation_type=RelationshipType.NONE, description="No verified relationship.")

    def normalize(self, skill: str) -> str:
        """Returns the canonical normalized lowercase name of a skill."""
        canonical, _ = self.normalize_skill(skill)
        return canonical.lower() if canonical else skill.lower()

    def get_relationship(self, target_skill: str, candidate_skill: str) -> SkillRelationship:
        """Alias for find_relationship."""
        return self.find_relationship(target_skill, candidate_skill)

    def is_known_skill(self, skill: str) -> bool:
        """Returns True if the skill exists in the ontology or alias knowledge graph."""
        _, is_known = self.normalize_skill(skill)
        return is_known


_global_ontology: SkillOntology | None = None


def get_skill_ontology() -> SkillOntology:
    global _global_ontology
    if _global_ontology is None:
        _global_ontology = SkillOntology()
    return _global_ontology
