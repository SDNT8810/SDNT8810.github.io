import { useParams, Link, Navigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { ArrowLeft, Github, ExternalLink, Play } from 'lucide-react';
import { projects } from '../data/content';

const ProjectDetail = () => {
  const { projectId } = useParams();
  const project = projects.find(p => p.id === projectId);

  if (!project) {
    return <Navigate to="/projects" replace />;
  }

  const YouTubeEmbed = ({ videoId }) => (
    <div className="aspect-video">
      <iframe
        src={`https://www.youtube.com/embed/${videoId}`}
        title="YouTube video player"
        frameBorder="0"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowFullScreen
        className="w-full h-full rounded-lg"
      ></iframe>
    </div>
  );

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Back Button */}
      <Button variant="ghost" asChild className="mb-8">
        <Link to="/projects">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Projects
        </Link>
      </Button>

      {/* Project Header */}
      <div className="space-y-6 mb-12">
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <h1 className="text-4xl font-bold">{project.title}</h1>
            <p className="text-xl text-muted-foreground">{project.shortDescription}</p>
          </div>
          {project.featured && (
            <Badge variant="default" className="text-sm">
              Featured Project
            </Badge>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap gap-4">
          {project.githubUrl && (
            <Button asChild>
              <a href={project.githubUrl} target="_blank" rel="noopener noreferrer">
                <Github className="mr-2 h-4 w-4" />
                View Code
              </a>
            </Button>
          )}
          {project.demoUrl && (
            <Button variant="outline" asChild>
              <a href={project.demoUrl} target="_blank" rel="noopener noreferrer">
                <ExternalLink className="mr-2 h-4 w-4" />
                Live Demo
              </a>
            </Button>
          )}
        </div>

        {/* Technologies */}
        <div className="flex flex-wrap gap-2">
          {project.technologies.map((tech) => (
            <Badge key={tech} variant="secondary">
              {tech}
            </Badge>
          ))}
        </div>
      </div>

      {/* Project Images */}
      {project.images && project.images.length > 0 && (
        <div className="space-y-6 mb-12">
          <h2 className="text-2xl font-bold">Project Gallery</h2>
          <div className="grid gap-6">
            {project.images.map((image, index) => (
              <div key={index} className="aspect-video bg-muted rounded-lg overflow-hidden">
                <img
                  src={image}
                  alt={`${project.title} - Image ${index + 1}`}
                  className="w-full h-full object-cover"
                />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* YouTube Videos */}
      {project.youtubeVideos && project.youtubeVideos.length > 0 && (
        <div className="space-y-6 mb-12">
          <h2 className="text-2xl font-bold flex items-center">
            <Play className="mr-2 h-6 w-6" />
            Project Videos
          </h2>
          <div className="grid gap-6">
            {project.youtubeVideos.map((videoId, index) => (
              <YouTubeEmbed key={index} videoId={videoId} />
            ))}
          </div>
        </div>
      )}

      {/* Project Description */}
      <div className="space-y-6 mb-12">
        <h2 className="text-2xl font-bold">About This Project</h2>
        <Card>
          <CardContent className="p-6">
            <p className="text-lg leading-relaxed">{project.description}</p>
          </CardContent>
        </Card>
      </div>

      {/* Placeholder for adding content */}
      <div className="space-y-6 mb-12">
        <h2 className="text-2xl font-bold">How to Add Content</h2>
        <Card>
          <CardContent className="p-6 space-y-4">
            <div className="bg-muted/50 p-4 rounded-lg">
              <h3 className="font-semibold mb-2">Adding Images:</h3>
              <p className="text-sm text-muted-foreground">
                1. Copy your images to the <code className="bg-muted px-1 rounded">src/assets</code> directory<br/>
                2. Update the <code className="bg-muted px-1 rounded">images</code> array in <code className="bg-muted px-1 rounded">src/data/content.js</code><br/>
                3. Use the path format: <code className="bg-muted px-1 rounded">/src/assets/your-image.jpg</code>
              </p>
            </div>
            <div className="bg-muted/50 p-4 rounded-lg">
              <h3 className="font-semibold mb-2">Adding YouTube Videos:</h3>
              <p className="text-sm text-muted-foreground">
                1. Get the video ID from your YouTube URL (e.g., from https://youtube.com/watch?v=ABC123, use "ABC123")<br/>
                2. Add the video ID to the <code className="bg-muted px-1 rounded">youtubeVideos</code> array in <code className="bg-muted px-1 rounded">src/data/content.js</code>
              </p>
            </div>
            <div className="bg-muted/50 p-4 rounded-lg">
              <h3 className="font-semibold mb-2">Adding New Projects:</h3>
              <p className="text-sm text-muted-foreground">
                1. Add a new project object to the <code className="bg-muted px-1 rounded">projects</code> array in <code className="bg-muted px-1 rounded">src/data/content.js</code><br/>
                2. Make sure to use a unique <code className="bg-muted px-1 rounded">id</code> for the project<br/>
                3. The project will automatically appear in the projects list and be accessible at <code className="bg-muted px-1 rounded">/projects/your-project-id</code>
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Related Projects */}
      <div className="space-y-6">
        <h2 className="text-2xl font-bold">Other Projects</h2>
        <div className="grid md:grid-cols-2 gap-6">
          {projects
            .filter(p => p.id !== project.id)
            .slice(0, 2)
            .map((relatedProject) => (
              <Card key={relatedProject.id} className="group hover:shadow-lg transition-all duration-300">
                <div className="aspect-video bg-muted rounded-t-lg overflow-hidden">
                  <img
                    src={relatedProject.images[0]}
                    alt={relatedProject.title}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                </div>
                <CardContent className="p-6">
                  <div className="space-y-4">
                    <div>
                      <h3 className="text-lg font-semibold mb-2">{relatedProject.title}</h3>
                      <p className="text-muted-foreground text-sm">{relatedProject.shortDescription}</p>
                    </div>
                    
                    <div className="flex flex-wrap gap-2">
                      {relatedProject.technologies.slice(0, 3).map((tech) => (
                        <Badge key={tech} variant="secondary" className="text-xs">
                          {tech}
                        </Badge>
                      ))}
                    </div>

                    <Button variant="outline" size="sm" asChild className="w-full">
                      <Link to={`/projects/${relatedProject.id}`}>
                        View Project
                      </Link>
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
        </div>
      </div>
    </div>
  );
};

export default ProjectDetail;

