import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ArrowRight, Search, Filter } from 'lucide-react';
import { Link } from 'react-router-dom';
import { projects } from '../data/content';

const Projects = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTech, setSelectedTech] = useState('');

  // Get all unique technologies
  const allTechnologies = [...new Set(projects.flatMap(project => project.technologies))].sort();

  // Filter projects based on search and technology
  const filteredProjects = projects.filter(project => {
    const matchesSearch = project.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         project.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         project.technologies.some(tech => tech.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesTech = selectedTech === '' || project.technologies.includes(selectedTech);
    
    return matchesSearch && matchesTech;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Header */}
      <div className="text-center space-y-4 mb-12">
        <h1 className="text-4xl lg:text-5xl font-bold">Projects</h1>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          A collection of my work in robotics, AI, embedded systems, and control engineering
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-col md:flex-row gap-4 mb-8">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search projects..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-muted-foreground" />
          <select
            value={selectedTech}
            onChange={(e) => setSelectedTech(e.target.value)}
            className="px-3 py-2 border border-border rounded-md bg-background text-foreground"
          >
            <option value="">All Technologies</option>
            {allTechnologies.map(tech => (
              <option key={tech} value={tech}>{tech}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Projects Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
        {filteredProjects.map((project) => (
          <Card key={project.id} className="group hover:shadow-lg transition-all duration-300">
            <div className="aspect-video bg-muted rounded-t-lg overflow-hidden">
              <img
                src={project.images[0]}
                alt={project.title}
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
              />
            </div>
            <CardContent className="p-6">
              <div className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-xl font-semibold">{project.title}</h3>
                    {project.featured && (
                      <Badge variant="default" className="text-xs">
                        Featured
                      </Badge>
                    )}
                  </div>
                  <p className="text-muted-foreground">{project.shortDescription}</p>
                </div>
                
                <div className="flex flex-wrap gap-2">
                  {project.technologies.slice(0, 4).map((tech) => (
                    <Badge key={tech} variant="secondary" className="text-xs">
                      {tech}
                    </Badge>
                  ))}
                  {project.technologies.length > 4 && (
                    <Badge variant="outline" className="text-xs">
                      +{project.technologies.length - 4} more
                    </Badge>
                  )}
                </div>

                <Button variant="outline" size="sm" asChild className="w-full">
                  <Link to={`/projects/${project.id}`}>
                    View Details <ArrowRight className="ml-2 h-3 w-3" />
                  </Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* No results */}
      {filteredProjects.length === 0 && (
        <div className="text-center py-12">
          <p className="text-muted-foreground">No projects found matching your criteria.</p>
          <Button
            variant="outline"
            onClick={() => {
              setSearchTerm('');
              setSelectedTech('');
            }}
            className="mt-4"
          >
            Clear Filters
          </Button>
        </div>
      )}

      {/* Call to Action */}
      <div className="text-center mt-16 p-8 bg-muted/30 rounded-lg">
        <h2 className="text-2xl font-bold mb-4">Interested in Collaboration?</h2>
        <p className="text-muted-foreground mb-6">
          I'm always open to discussing new opportunities and innovative projects.
        </p>
        <Button size="lg" asChild>
          <a href={`mailto:${projects[0] ? 'davoudnikkhouy@gmail.com' : ''}`}>
            Get In Touch
          </a>
        </Button>
      </div>
    </div>
  );
};

export default Projects;

