import click

from art import logo
from utils import (check_order_details, cls, create_batch_order_with_body,
                   create_batch_order_with_query)


@click.group()
def cli():
    """Click-specific function, initiates a group."""
    pass


@cli.command()
def gui():
    """Shows GUI."""
    print(logo)

    while True:
        choice = input(
            "\nPlease choose one of the following:\n1 - Create Batch Order Using A Body\n2 - Create Batch Order Using "
            "A Query\n3 - Check Order Details\n4 - Exit\n"
        )
        cls()
        match choice:
            case "1":
                create_batch_order_with_body()
            case "2":
                create_batch_order_with_query()
            case "3":
                while True:
                    try:
                        order_id = int(input("Please provide order id : "))
                        check_order_details(order_id)
                        break
                    except ValueError:
                        print("You entered a non-integer value, please try again.")
                        continue
            case "4":
                break


@cli.command()
def create_order_with_body():
    """Creates BatchOrder Using Provided By User Body."""
    create_batch_order_with_body()


@cli.command()
@click.option("--hours", help="Specify hour mark to look back for products")
def create_order_with_query(hours: str):
    """Creates BatchOrder Using Provided By User Query."""
    if hours:
        try:
            hours = int(hours)
        except ValueError:
            print("You entered a non-integer value, please try again.")
        else:
            create_batch_order_with_query(hours)
    else:
        create_batch_order_with_query()


cli = click.CommandCollection(sources=[cli])

if __name__ == "__main__":
    cli()
