import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ArrowRight, Download, MapPin, Phone, Mail } from 'lucide-react';
import { Link } from 'react-router-dom';
import { personalInfo, projects } from '../data/content';

const Home = () => {
  const featuredProjects = projects.filter(project => project.featured).slice(0, 3);

  return (
    <div className="space-y-20">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-primary/5 via-background to-secondary/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 lg:py-32">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-8">
              <div className="space-y-4">
                <h1 className="text-4xl lg:text-6xl font-bold tracking-tight">
                  Hi, I'm{' '}
                  <span className="text-primary">{personalInfo.name}</span>
                </h1>
                <h2 className="text-xl lg:text-2xl text-muted-foreground">
                  {personalInfo.title}
                </h2>
              </div>
              
              <p className="text-lg text-muted-foreground leading-relaxed">
                {personalInfo.about}
              </p>

              <div className="flex flex-col sm:flex-row gap-4">
                <Button size="lg" asChild>
                  <Link to="/projects">
                    View My Work <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
                <Button variant="outline" size="lg">
                  <Download className="mr-2 h-4 w-4" />
                  Download CV
                </Button>
              </div>

              <div className="flex flex-wrap gap-6 text-sm text-muted-foreground">
                <div className="flex items-center">
                  <MapPin className="h-4 w-4 mr-2" />
                  Milan, Italy
                </div>
                <div className="flex items-center">
                  <Phone className="h-4 w-4 mr-2" />
                  {personalInfo.phone}
                </div>
                <div className="flex items-center">
                  <Mail className="h-4 w-4 mr-2" />
                  {personalInfo.email}
                </div>
              </div>
            </div>

            <div className="relative">
              <div className="w-full h-96 bg-gradient-to-br from-primary/20 to-secondary/20 rounded-2xl flex items-center justify-center">
                <div className="text-center space-y-4">
                  <div className="w-32 h-32 bg-primary/10 rounded-full flex items-center justify-center mx-auto">
                    <span className="text-4xl font-bold text-primary">DN</span>
                  </div>
                  <p className="text-muted-foreground">Professional Photo Coming Soon</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Projects */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center space-y-4 mb-12">
          <h2 className="text-3xl lg:text-4xl font-bold">Featured Projects</h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Explore some of my recent work in robotics, AI, and embedded systems
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {featuredProjects.map((project) => (
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
                    <h3 className="text-xl font-semibold mb-2">{project.title}</h3>
                    <p className="text-muted-foreground">{project.shortDescription}</p>
                  </div>
                  
                  <div className="flex flex-wrap gap-2">
                    {project.technologies.slice(0, 3).map((tech) => (
                      <Badge key={tech} variant="secondary" className="text-xs">
                        {tech}
                      </Badge>
                    ))}
                    {project.technologies.length > 3 && (
                      <Badge variant="outline" className="text-xs">
                        +{project.technologies.length - 3} more
                      </Badge>
                    )}
                  </div>

                  <Button variant="outline" size="sm" asChild className="w-full">
                    <Link to={`/projects/${project.id}`}>
                      Learn More <ArrowRight className="ml-2 h-3 w-3" />
                    </Link>
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="text-center mt-12">
          <Button variant="outline" size="lg" asChild>
            <Link to="/projects">
              View All Projects <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </Button>
        </div>
      </section>

      {/* Quick Stats */}
      <section className="bg-muted/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div className="space-y-2">
              <div className="text-3xl font-bold text-primary">5+</div>
              <div className="text-sm text-muted-foreground">Years Experience</div>
            </div>
            <div className="space-y-2">
              <div className="text-3xl font-bold text-primary">6+</div>
              <div className="text-sm text-muted-foreground">Projects Completed</div>
            </div>
            <div className="space-y-2">
              <div className="text-3xl font-bold text-primary">5</div>
              <div className="text-sm text-muted-foreground">Publications</div>
            </div>
            <div className="space-y-2">
              <div className="text-3xl font-bold text-primary">2</div>
              <div className="text-sm text-muted-foreground">Degrees</div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;

