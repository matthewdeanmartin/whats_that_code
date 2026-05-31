class Greeter
  def initialize(name)
    @name = name
  end

  def greet
    puts "hello, #{@name}"
  end
end

Greeter.new("world").greet
